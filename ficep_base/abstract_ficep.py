# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml import etree
import logging

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID

_logger = logging.getLogger(__name__)


INVALIDATE_ERROR = _('Invalidation impossible, at least one dependency is still active')


def format_email(value):
    """
    ============
    format_email
    ============
    :type value: char
    :rtype: char
    :rparam value: value without space and in lower case
    """
    value = value.lower().strip()
    value = value.replace(' ', '')
    return value


class abstract_ficep_model(orm.AbstractModel):

    _name = 'abstract.ficep.model'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Abstract Ficep Model'

    _allowed_inactive_link_models = []
    _inactive_cascade = False

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
        vals.update(self.get_fields_to_update(cr, uid, 'deactivate', context=context))
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
        vals.update(self.get_fields_to_update(cr, uid, 'activate', context=context))
        return self.write(cr, uid, ids, vals, context=context)

    def get_fields_to_update(self, cr, uid, mode, context=None):
        """
        ====================
        get_fields_to_update
        ====================
        Depending on a mode, builds a dictionary allowing to update validity fields
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
        'expire_date': fields.datetime('Expiration Date', readonly=True, track_visibility='onchange'),
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
        Check if object can be desactivated, dependencies must be desactivated before
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        invalidate_ids = list(ids)
        ficep_models = self.browse(cr, uid, invalidate_ids, context=context)
        for ficep_model in ficep_models:
            if not ficep_model.expire_date:
                invalidate_ids.remove(ficep_model.id)

        if invalidate_ids:
            rels_dict = self.pool.get('ir.model')._get_active_relations(cr, uid, invalidate_ids, self._name, context=context)

            if len(rels_dict) > 0:
                for k in rels_dict.keys():
                    _logger.info('Remaining active m2o for %s(%s): %s', self._name, k, rels_dict[k])
                return False

        return True

    def _invalidate_active_relations(self, cr, uid, ids, context=None):
        """
        =============================
        _invalidate_actives_relations
        =============================
        Invalidate all dependencies of ids object
        :rparam: True if no error
                 False otherwise
        :rtype: boolean
        """
        invalidate_ids = isinstance(ids, (long, int)) and [ids] or ids
        if invalidate_ids:
            rels_dict = self.pool.get('ir.model')._get_active_relations(cr, uid, invalidate_ids, self._name, context=context, with_ids=True)
            for relation_models in rels_dict.values():
                for relation, relation_ids in relation_models.iteritems():
                    relation_object = self.pool.get(relation)
                    if hasattr(relation_object, 'action_invalidate'):
                        relation_object.action_invalidate(cr, uid, relation_ids, context=context)
                    else:
                        if relation == 'mail.followers':
                            relation_object.unlink(cr, uid, relation_ids, context=context)
                        elif hasattr(relation_object, 'active'):
                            relation_object.write(cr, uid, relation_ids, {'active': False}, context=context)

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
        index_def = "CREATE UNIQUE INDEX %s_unique_idx ON %s USING btree (%s) WHERE (active IS TRUE)" % \
                    (self._table, self._table, self._unicity_keys)
        cr.execute("""SELECT indexdef
                      FROM pg_indexes
                      WHERE tablename = '%s' and indexname = '%s_unique_idx'""" % \
                   (self._table, self._table))
        sql_res = cr.dictfetchone()
        if sql_res:
            if sql_res['indexdef'] != index_def:
                cr.execute("DROP INDEX %s_unique_idx" % (self._table,))
            else:
                createit = False

        if createit:
            cr.execute(index_def)

# orm methods

    def create(self, cr, uid, vals, context=None):
        """
        Do not add creator to followers nor track message on create
        Disable tracking if possible: when testing, installing, migrating, ...
        """
        ctx = dict(context or {}, mail_no_autosubscribe=True)
        if ctx.get('install_mode') or not 'uid' in ctx:
            ctx['tracking_disable'] = True
        if not ctx.get('tracking_disable'):
            ctx.update({
                'mail_create_nosubscribe': True,
                'mail_notrack': True,
            })
        new_id = super(abstract_ficep_model, self).create(cr, uid, vals, context=ctx)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        """
        Disable tracking if possible: when testing, installing, migrating, ...
        """
        ctx = dict(context or {}, mail_no_autosubscribe=True)
        if ctx.get('install_mode') or not 'uid' in ctx:
            ctx['tracking_disable'] = True
        mode = False
        if 'active' in vals:
            mode = 'activate' if vals['active'] else 'deactivate'
            vals.update(self.get_fields_to_update(cr, uid, mode, context=ctx))
        if mode == 'deactivate' and self._inactive_cascade:
            mail_follower_object = self.pool['mail.followers']
            follower_ids = mail_follower_object.search(cr, uid, [('res_model', '=', self._name), ('res_id', 'in', ids)], context=context)
            if follower_ids:
                mail_follower_object.unlink(
                    cr, uid, follower_ids, context=context)
            self._invalidate_active_relations(cr, uid, ids, context=ctx)
        res = super(abstract_ficep_model, self).write(cr, uid, ids, vals, context=ctx)
        return res

    def message_auto_subscribe(self, cr, uid, ids, updated_fields, context=None, values=None):
        ctx = context or {}
        if ctx.get('mail_no_autosubscribe'):
            return True
        res = super(abstract_ficep_model, self).message_auto_subscribe(cr, uid, ids, updated_fields, context=ctx, values=values)
        return res

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Reset some fields to their initial values
        """
        default = default or {}
        default.update(self.get_fields_to_update(cr, uid, 'activate', context=context))
        res = super(abstract_ficep_model, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        * Add the "popup" item into the context if the form will be shown as a popup
        * Generate a domain on all fields to make the form readonly when document is inactive
        * Work around the automatic form generation when it is inherited from an other model
        * Wrongly handle by oe, add manually the readonly attribute to message_ids if needed
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
                          ORDER BY priority LIMIT 1""", (self._name, view_type))
            sql_res = cr.dictfetchone()
            if not sql_res:
                cr.execute("""SELECT id
                              FROM ir_ui_view
                              WHERE model=%s AND type=%s
                              ORDER BY priority LIMIT 1""", (self._name, view_type))
                sql_res = cr.dictfetchone()
                if sql_res:
                    # force this existing view
                    view_id = sql_res['id']
                elif view_type in ['tree', 'search']:
                    # Heuristic at this point: maybe an abstract search or tree view is declared on an ir.act.window
                    col = view_type == 'search' and 'search_view_id' or 'view_id'
                    cr.execute("""SELECT %s as v
                                  FROM ir_act_window, ir_ui_view i
                                  WHERE res_model=%%s AND i.id = %s
                                  ORDER BY priority LIMIT 1""" % (col, col), (self._name, ))
                    sql_res = cr.dictfetchone()
                    if sql_res:
                        # force this existing view
                        view_id = sql_res['v']

        res = super(abstract_ficep_model, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

        if view_type == 'form' and not context.get('in_ficep_user'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='message_ids']"):
                node.set('readonly', '1')
            res['arch'] = etree.tostring(doc)
        return res

    def get_formview_id(self, cr, uid, id, context=None):
        """ Return a view id to open the document with.

            :param int id: id of the document to open
        """
        view_ids = self.pool['ir.ui.view'].search(cr, uid,
                                            [('model', '=', self._name),
                                             ('type', '=', 'form')],
                                             limit=1, context=context)
        return view_ids[0] if view_ids else False

    def display_object_in_form_view(self, cr, uid, object_id, context=None):
        """
        Return the object (with given id) in the default form view
        """
        return self.get_formview_action(cr, uid, object_id, context=None)

    def get_relation_column_name(self, cr, uid, relation_model, context=None):
        return self.pool.get('ir.model')._get_relation_column_name(cr, uid, self._name, relation_model, context=context)

# Replace the orm.transfer_node_to_modifiers functions.

original_transfer_node_to_modifiers = orm.transfer_node_to_modifiers
XP = "//field[not(ancestor::div[(@name='dev') or (@name='chat')])]" \
     "[not(ancestor::field)]"


def transfer_node_to_modifiers(node, modifiers, context=None, in_tree_view=False):
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
