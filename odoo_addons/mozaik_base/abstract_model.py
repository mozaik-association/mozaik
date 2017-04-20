# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml import etree
import logging

from openerp import api
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)


INVALIDATE_ERROR = _(
    'Invalidation impossible, at least one dependency is still active')


class mozaik_abstract_model(orm.AbstractModel):

    _name = 'mozaik.abstract.model'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'mozaik.abstract.model'

    _allowed_inactive_link_models = []
    _inactive_cascade = False

    def _format_message(self, cr, uid, message_description='', context=None):
        message = ''
        if message_description:
            message = '<span>%s</span>' % message_description
        return message

    def _message_post(self, cr, uid, object_id, subtype='', context=None):
        subtype_rec = self.pool.get('ir.model.data').xmlid_to_object(
            cr, uid, subtype, context=context)
        description = subtype_rec and subtype_rec.description or ''
        message = self._format_message(
            cr, uid, message_description=description, context=context)
        self.message_post(
            cr, uid, object_id, body=message, subtype=subtype, context=context)

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        =================
        action_invalidate
        =================
        Invalidates an object
        :rparam: True
        :rtype: boolean
        Note: Argument vals must be the last in the signature
        """
        vals = vals or {}
        vals.update(self.get_fields_to_update(
            cr, uid, 'deactivate', context=context))
        return self.write(cr, uid, ids, vals, context=context)

    def action_revalidate(self, cr, uid, ids, context=None, vals=None):
        """
        ===============
        action_revalidate
        ===============
        Reactivates an object by setting
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        vals.update(self.get_fields_to_update(
            cr, uid, 'activate', context=context))
        return self.write(cr, uid, ids, vals, context=context)

    def get_fields_to_update(self, cr, uid, mode, context=None):
        """
        ====================
        get_fields_to_update
        ====================
        Depending on a mode, builds a dictionary allowing to update validity
        fields
        :rparam: fields to update
        :rtype: dictionary
        """
        res = {}
        if mode == 'deactivate':
            res.update({
                'active': False,
                'expire_date': fields.datetime.now(),
            })
        if mode == 'activate':
            res.update({
                'active': True,
                'expire_date': False,
            })
        return res

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', readonly=True,
                                       track_visibility='onchange'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
        'expire_date': False,
    }

# constraints

    def _check_invalidate(self, cr, uid, ids, context=None):
        """
        =================
        _check_invalidate
        =================
        Check if object can be desactivated, dependencies must be desactivated
        before
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        uid = SUPERUSER_ID
        invalidate_ids = list(ids)
        recs = self.browse(cr, uid, invalidate_ids, context=context)
        for rec in recs:
            if not rec.expire_date:
                invalidate_ids.remove(rec.id)

        if invalidate_ids:
            im_obj = self.pool['ir.model']
            rels_dict = im_obj._get_active_relations(
                cr, uid, invalidate_ids, self._name, context=context)

            if len(rels_dict) > 0:
                for k in rels_dict.keys():
                    _logger.info(
                        'Remaining active m2o for %s(%s): %s',
                        self._name, k, rels_dict[k])
                return False

        return True

    def _invalidate_active_relations(self, cr, uid, ids, context=None):
        """
        Invalidate all dependencies of object ids
        """
        invalidate_ids = isinstance(ids, (long, int)) and [ids] or ids
        if invalidate_ids:
            rels_dict = self.pool['ir.model']._get_active_relations(
                cr, uid, invalidate_ids, self._name, context=context,
                with_ids=True)
            for relation_models in rels_dict.values():
                for relation, relation_ids in relation_models.iteritems():
                    relation_object = self.pool.get(relation)
                    if hasattr(relation_object, 'action_invalidate'):
                        relation_object.action_invalidate(
                            cr, uid, relation_ids, context=context)
                    elif relation in ['mail.followers', 'mail.notification']:
                        # Unlink obsolete followers. Sudo rights are required.
                        relation_object.unlink(
                            cr, SUPERUSER_ID, relation_ids, context=context)
                    elif hasattr(relation_object, 'active'):
                        relation_object.write(
                            cr, uid, relation_ids,
                            {'active': False}, context=context)

    _constraints = [
        (_check_invalidate, INVALIDATE_ERROR, ['expire_date'])
    ]

    _unicity_keys = None

    def init(self, cr):
        if not self._auto:
            return

        if not self._unicity_keys:
            _logger.warn('No _unicity_keys specified for model %s', self._name)
            return

        if self._unicity_keys == 'N/A':
            return

        createit = True
        index_def = """CREATE UNIQUE INDEX %s_unique_idx ON %s
                      USING btree (%s) WHERE (active IS TRUE)""" % \
                    (self._table, self._table, self._unicity_keys)
        cr.execute("""SELECT indexdef
                      FROM pg_indexes
                      WHERE tablename = '%s' and indexname = '%s_unique_idx'
                    """ % (self._table, self._table))
        sql_res = cr.dictfetchone()
        if sql_res:
            if sql_res['indexdef'] != index_def:
                cr.execute("DROP INDEX %s_unique_idx" % (self._table,))
            else:
                createit = False

        if createit:
            cr.execute(index_def)

# orm methods

    def _apply_ir_rules(self, cr, uid, query, mode='read', context=None):
        context = context or {}
        if 'apply_for_%s' % mode in context:
            res = super(mozaik_abstract_model, self)._apply_ir_rules(
                cr, uid, query, mode=context['apply_for_%s' % mode],
                context=context)
        else:
            res = super(mozaik_abstract_model, self)._apply_ir_rules(
                cr, uid, query, mode=mode, context=context)
        return res

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        Do not add creator to followers nor track message on create
        Disable tracking if possible: when testing, installing, migrating, ...
        """
        ctx = dict(self.env.context, mail_no_autosubscribe=True)
        if ctx.get('install_mode') or self.env.all.mode:
            ctx['tracking_disable'] = True
        if not ctx.get('tracking_disable'):
            ctx.update({
                'mail_create_nosubscribe': True,
                'mail_notrack': True,
            })
        # Work around the optimization algorithm introduced in the setter of
        # one2many fields, it breaks the record rules check at the end of
        # model._create because all data needed to evaluate rules are not
        # already available
        self.env.all.recompute = True

        new_id = super(
            mozaik_abstract_model, self.with_context(ctx)).create(vals)

        if ctx.get('install_mode') and vals.get('create_date'):
            q = 'update %s set create_date=%%s where id=%%s' % self._table
            self.env.cr.execute(q, (vals['create_date'], new_id.id))
        return new_id.with_context(self.env.context)

    @api.multi
    def write(self, vals):
        """
        Disable tracking if possible: when testing, installing, migrating, ...
        """
        ctx = dict(self.env.context, mail_no_autosubscribe=True)
        if ctx.get('install_mode') or self.env.all.mode:
            ctx['tracking_disable'] = True
        self = self.with_context(ctx)
        if 'active' in vals:
            mode = 'activate' if vals['active'] else 'deactivate'
            expire_date = vals.get('expire_date', False)
            vals.update(self.get_fields_to_update(mode))
            if mode == 'deactivate':
                if expire_date:
                    vals['expire_date'] = expire_date
                if self._inactive_cascade:
                    self._invalidate_active_relations()
        res = super(mozaik_abstract_model, self).write(vals)
        return res

    def step_workflow(self, cr, uid, ids, context=None):
        """
        Trap ValueError exceptions and transform them to
        a classic Access Denied error avoiding the stack trace
        generated by safe_eval in case of security restrictions
        """
        try:
            return super(mozaik_abstract_model, self).step_workflow(
                cr, uid, ids, context=context)
        except ValueError, e:
            s = e.message.split('\n')
            if len(s) != 2:
                raise
            raise except_orm(
                _('Access Denied'),
                _('The requested operation cannot be completed due to '
                  'security restrictions\n'
                  '(Document type: %s, Operation: %s)\n'
                  'or due to some undefined names while evaluating:\n%s') %
                (self._description, 'read', s[1]))

    def message_auto_subscribe(self, cr, uid, ids, updated_fields,
                               context=None, values=None):
        ctx = context or {}
        if ctx.get('mail_no_autosubscribe'):
            return True
        res = super(mozaik_abstract_model, self).message_auto_subscribe(
            cr, uid, ids, updated_fields, context=ctx, values=values)
        return res

    def message_subscribe(
            self, cr, uid, ids, partner_ids, subtype_ids=None, context=None):
        """
        Update followers with sudo rights to avoid security issues
        (!! Thanks odoo for this nice implementation !!)
        """
        uid = SUPERUSER_ID
        res = super(mozaik_abstract_model, self).message_subscribe(
            cr, uid, ids, partner_ids, subtype_ids, context=context)
        return res

    def reset_followers(
            self, cr, uid, ids, except_fol_ids=None, context=None):
        """
        Reset followers list associated to a document
        """
        uid = SUPERUSER_ID
        fol_obj = self.pool['mail.followers']
        dom = except_fol_ids and [
            ('partner_id', 'not in', except_fol_ids),
        ] or []
        dom = dom + [
            ('res_model', '=', self._name),
            ('res_id', 'in', ids),
        ]
        fol_ids = fol_obj.search(
            cr, uid, dom, context=context)
        return fol_obj.unlink(cr, uid, fol_ids, context=context)

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Reset some fields to their initial values
        """
        default = default or {}
        default.update(
            self.get_fields_to_update(cr, uid, 'activate', context=context))
        res = super(mozaik_abstract_model, self).copy_data(
            cr, uid, ids, default=default, context=context)
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
        * Add the "popup" item into the context if the form will be shown as a
          popup
        * Generate a domain on all fields to make the form readonly when
          document is inactive
        * Work around the automatic form generation when it is inherited from
          an other model
        * Wrongly handle by oe, add manually the readonly attribute to
          message_ids if needed
        """
        context = context or {}

        if view_type == 'form':
            if not toolbar:
                context.update(popup=True)
            if uid != SUPERUSER_ID and not context.get('is_developper'):
                context.update(add_readonly_condition=True)

        if not view_id and not context.get('%s_view_ref' % view_type):
            cr.execute("""SELECT id
                          FROM ir_ui_view
                          WHERE model=%s AND type=%s AND inherit_id IS NULL
                          ORDER BY priority LIMIT 1""",
                       (self._name, view_type))
            sql_res = cr.dictfetchone()
            if not sql_res:
                cr.execute("""SELECT id
                              FROM ir_ui_view
                              WHERE model=%s AND type=%s
                              ORDER BY priority LIMIT 1""",
                           (self._name, view_type))
                sql_res = cr.dictfetchone()
                if sql_res:
                    # force this existing view
                    view_id = sql_res['id']
                elif view_type in ['tree', 'search']:
                    # Heuristic at this point: maybe an abstract search or
                    # tree view is declared on an ir.act.window
                    col = view_type == 'search' and \
                        'search_view_id' or 'view_id'
                    cr.execute("""SELECT %s as v
                                  FROM ir_act_window, ir_ui_view i
                                  WHERE res_model=%%s AND i.id = %s
                                  ORDER BY priority LIMIT 1""" % (col, col),
                               (self._name, ))
                    sql_res = cr.dictfetchone()
                    if sql_res:
                        # force this existing view
                        view_id = sql_res['v']

        res = super(mozaik_abstract_model, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)

        if view_type == 'form' and not context.get('in_mozaik_user'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='message_ids']"):
                node.set('readonly', '1')
            res['arch'] = etree.tostring(doc)
        return res

# public methods

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, context=None, **kwargs):
        """
        Do not auto-subscribe
        """
        ctx = dict(context or {}, mail_create_nosubscribe=True)
        ctx.pop('mail_post_autofollow', None)
        ctx['is_notification'] = True
        return super(mozaik_abstract_model, self).message_post(
            cr, uid, thread_id, context=ctx, **kwargs)

    def get_formview_id(self, cr, uid, id, context=None):
        """ Return a view id to open the document with.

            :param int id: id of the document to open
        """
        view_ids = self.pool['ir.ui.view'].search(
            cr, uid, [('model', '=', self._name),
                      ('type', '=', 'form')],
            limit=1, context=context)
        return view_ids[0] if view_ids else False

    def display_object_in_form_view(self, cr, uid, object_id, context=None):
        """
        Return the object (with given id) in the default form view
        """
        return self.get_formview_action(cr, uid, object_id, context=context)

    def get_relation_column_name(self, cr, uid, relation_model, context=None):
        return self.pool['ir.model']._get_relation_column_name(
            cr, uid, self._name, relation_model, context=context)

# Replace the orm.transfer_node_to_modifiers functions.

original_transfer_node_to_modifiers = orm.transfer_node_to_modifiers
XP = "//field[not(ancestor::div[(@name='dev') or (@name='chat')])]" \
     "[not(ancestor::field)]"


def transfer_node_to_modifiers(node, modifiers, context=None,
                               in_tree_view=False):
    '''
    Add conditions on usefull fields (but chatting fields) to make
    the form readonly if the document is inactive
    '''
    fct_src = original_transfer_node_to_modifiers
    trace = False

    if context and context.get('add_readonly_condition'):
        context.pop('add_readonly_condition')

        if trace:
            # etree.tostring(node)
            pass
        if node.xpath("//field[@name='active'][not(ancestor::field)]"):
            for nd in node.xpath(XP):
                if nd.get('readonly', '') == '1':
                    continue
                attrs_str = nd.get('attrs') or '{}'
                attrs = eval(attrs_str)
                if attrs.get('readonly'):
                    dom = str(attrs.get('readonly'))
                    if len(dom.split("'active'")) > 1:
                        continue
                nd.set('aroc', '1')

    aroc = node.get('aroc')
    if aroc:
        node.attrib.pop('aroc')
        aroc = not modifiers.get('readonly', False)
    if aroc:
        attrs_str = node.get('attrs') or '{}'
        attrs = eval(attrs_str)
        if attrs.get('readonly'):
            dom = str(attrs.get('readonly'))[1:-1]
            dom = "['|', ('active', '=', False), %s]" % dom
            attrs['readonly'] = eval(dom)
        else:
            attrs['readonly'] = [('active', '=', False)]
        attrs = str(attrs)
        node.set('attrs', attrs)
        if trace:
            _logger.warning(
                'Field %s - attrs before: %s - after: %s',
                node.get('name'), attrs_str, attrs)

    return fct_src(node, modifiers, context=context, in_tree_view=in_tree_view)

orm.transfer_node_to_modifiers = transfer_node_to_modifiers
