# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from lxml import etree
import logging

from odoo import api, fields, models, _  # , SUPERUSER_ID
from odoo.exceptions import ValidationError  # except_orm

_logger = logging.getLogger(__name__)


INVALIDATE_ERROR = _(
    'Invalidation impossible, at least one dependency is still active')


# def _patch_get_followers(self, cr, uid, ids, name, arg, context=None):
#     """
#     Monkey patch _get_followers() to reapply security on result followers
#     """
#     res = self._get_followers(cr, uid, ids, name, arg, context=context)
#     ids = []
#     for v in res.itervalues():
#         ids += v['message_follower_ids']
#     # reapply security to avoid to prefetch later unauthorized followers
#     ids = set(self.env['res.partner'].search(
#         cr, uid, [('id', 'in', ids)], context=context))
#     for v in res.itervalues():
#         v['message_follower_ids'] = list(set(v['message_follower_ids']) & ids)
#     return res


class MozaikAbstractModel(models.AbstractModel):

    _name = 'mozaik.abstract.model'
    _inherit = ['mail.thread', ]#'ir.needaction_mixin']
    _description = 'mozaik.abstract.model'

    _allowed_inactive_link_models = []
    _inactive_cascade = False

    # id = fields.Integer('ID', readonly=True) # TODO fields alwayse defined
    # create_date = fields.Datetime('Creation Date', readonly=True)
    expire_date = fields.Datetime(
        'Expiration Date', readonly=True, default=False,
        track_visibility='onchange') # TODO: should not be in dep of mail
    active = fields.Boolean('Active', default=True)

    # @api.multi
    # def _message_post(self, subtype):
    #     subtype_rec = self.env.ref(subtype)
    #     description = subtype_rec.description  if subtype_rec else  ''
    #     message = ''
    #     if description:
    #         message = '<span>%s</span>' % description
    #     self.message_post(body=message, subtype=subtype)

    @api.multi
    def action_invalidate(self, vals=None):
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
        vals.update(self.get_fields_to_update('deactivate'))
        return self.write(vals)

    @api.multi
    def action_revalidate(self, vals=None):
        """
        ===============
        action_revalidate
        ===============
        Reactivates an object by setting
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        vals.update(self.get_fields_to_update('activate'))
        return self.write(vals)

    @api.model
    def get_fields_to_update(self, mode):
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

# constraints
    @api.multi
    @api.depends('expire_date')
    def _check_invalidate(self):
        """
        =================
        _check_invalidate
        =================
        Check if object can be desactivated, dependencies must be desactivated
        before
        """
        self = self.sudo()  # TODO
        invalidate_ids = self
        for rec in self:
            if not rec.expire_date:
                invalidate_ids -= rec

        if invalidate_ids:
            im_obj = self.env['ir.model']
            rels_dict = im_obj._get_active_relations(invalidate_ids)

            if rels_dict:
                for k in rels_dict.keys():
                    _logger.info(
                        'Remaining active m2o for %s(%s): %s',
                        self._name, k, rels_dict[k])
                raise ValidationError(INVALIDATE_ERROR)

    @api.multi
    def _invalidate_active_relations(self):
        """
        Invalidate all dependencies of object ids
        """
        if self:
            rels_dict = self.env['ir.model']._get_active_relations(
                self, with_ids=True)
            for relation_models in rels_dict.values():
                for relation, relation_ids in relation_models.iteritems():
                    relation_object = self.env.get(relation)
                    if hasattr(relation_object, 'action_invalidate'):
                        relation_ids.action_invalidate()
                    elif relation in ['mail.followers', 'mail.notification']: # TODO: should not be in dep of mail
                        # Unlink obsolete followers. Sudo rights are required.
                        relation_ids.sudo().unlink()
                    elif hasattr(relation_object, 'active'):
                        relation_ids.write({'active': False})

    _unicity_keys = None

    def init(self):
        if not self._auto:
            return

        if not self._unicity_keys:
            _logger.warning('No _unicity_keys specified for model %s', self._name)
            return

        if self._unicity_keys == 'N/A':
            return

        cr = self.env.cr
        unicity = " ".join(self._unicity_keys.split())
        createit = True
        index_def = "CREATE UNIQUE INDEX %s_unique_idx ON %s " \
                    "USING btree (%s) WHERE (active IS TRUE)" % \
                    (self._table, self._table, unicity)
        cr.execute("""SELECT indexdef
                      FROM pg_indexes
                      WHERE tablename = '%s' and indexname = '%s_unique_idx'
                    """ % (self._table, self._table))
        sql_res = cr.dictfetchone()
        if sql_res:
            previous = sql_res['indexdef'].replace(' ON public.', ' ON ')
            if previous != index_def:
                _logger.info(
                    'Rebuild index %s_unique_idx:\n%s\n%s',
                    self._name, previous, index_def)
                cr.execute("DROP INDEX %s_unique_idx" % (self._table,))
            else:
                createit = False

        if createit:
            cr.execute(index_def)
#
    # @api.model_cr
    # def _register_hook(self):
    #     """
    #     Change function pointer of non heritable compute method
    #     """
    #     init_res = super()._register_hook()
    #     self._fields['message_is_follower']._fnct = _patch_get_followers
    #     self._fields['message_follower_ids']._fnct = _patch_get_followers
    #     return init_res
#
# # orm methods
#
#     def _apply_ir_rules(self, cr, uid, query, mode='read', context=None):
#         context = context or {}
#         if 'apply_for_%s' % mode in context:
#             res = super(mozaik_abstract_model, self)._apply_ir_rules(
#                 cr, uid, query, mode=context['apply_for_%s' % mode],
#                 context=context)
#         else:
#             res = super(mozaik_abstract_model, self)._apply_ir_rules(
#                 cr, uid, query, mode=mode, context=context)
#         return res
#
#     @api.model
#     @api.returns('self', lambda value: value.id)
#     def create(self, vals):
#         """
#         Do not add creator to followers nor track message on create
#         Disable tracking if possible: when testing, installing, migrating, ...
#         """
#         ctx = dict(self.env.context)
#         if ctx.get('install_mode') or self.env.all.mode:
#             ctx['tracking_disable'] = True
#         if not ctx.get('tracking_disable'):
#             ctx.update({
#                 'mail_create_nosubscribe': True,
#                 'mail_notrack': True,
#             })
#         # Work around the optimization algorithm introduced in the setter of
#         # one2many fields, it breaks the record rules check at the end of
#         # model._create because all data needed to evaluate rules are not
#         # already available
#         self.env.all.recompute = True
#
#         new_id = super(
#             MozaikAbstractModel, self.with_context(ctx)).create(vals)
#
#         if ctx.get('install_mode') and vals.get('create_date'):
#             q = 'update %s set create_date=%%s where id=%%s' % self._table
#             self.env.cr.execute(q, (vals['create_date'], new_id.id))
#         return new_id.with_context(self.env.context)
#
#     @api.multi
#     def write(self, vals):
#         """
#         Disable tracking if possible: when testing, installing, migrating, ...
#         """
#         ctx = dict(self.env.context)
#         if ctx.get('install_mode') or self.env.all.mode:
#             ctx['tracking_disable'] = True
#         self = self.with_context(ctx)
#         if 'active' in vals:
#             mode = 'activate' if vals['active'] else 'deactivate'
#             expire_date = vals.get('expire_date', False)
#             vals.update(self.get_fields_to_update(mode))
#             if mode == 'deactivate':
#                 if expire_date:
#                     vals['expire_date'] = expire_date
#                 if self._inactive_cascade:
#                     self._invalidate_active_relations()
#         res = super(mozaik_abstract_model, self).write(vals)
#         return res
#
#     def step_workflow(self, cr, uid, ids, context=None):
#         """
#         Trap ValueError exceptions and transform them to
#         a classic Access Denied error avoiding the stack trace
#         generated by safe_eval in case of security restrictions
#         """
#         try:
#             return super(mozaik_abstract_model, self).step_workflow(
#                 cr, uid, ids, context=context)
#         except ValueError, e:
#             s = e.message.split('\n')
#             if len(s) != 2:
#                 raise
#             raise except_orm(
#                 _('Access Denied'),
#                 _('The requested operation cannot be completed due to '
#                   'security restrictions\n'
#                   '(Document type: %s, Operation: %s)\n'
#                   'or due to some undefined names while evaluating:\n%s') %
#                 (self._description, 'read', s[1]))
#
#     @api.model
#     def _message_get_auto_subscribe_fields(
#             self, vals, auto_follow_fields=None):
#         """ Disable auto subscribe by field """
#         return []
#
#     @api.multi
#     def message_subscribe(
#             self, partner_ids, subtype_ids=None):
#         """
#         Update followers with sudo rights to avoid security issues
#         """
#         res = super(MozaikAbstractModel, self.sudo()).message_subscribe(
#             partner_ids, subtype_ids=subtype_ids)
#         return res
#
#     def reset_followers(
#             self, cr, uid, ids, except_fol_ids=None, context=None):
#         """
#         Reset followers list associated to a document
#         """
#         uid = SUPERUSER_ID
#         fol_obj = self.env['mail.followers']
#         dom = except_fol_ids and [
#             ('partner_id', 'not in', except_fol_ids),
#         ] or []
#         dom = dom + [
#             ('res_model', '=', self._name),
#             ('res_id', 'in', ids),
#         ]
#         fol_ids = fol_obj.search(
#             cr, uid, dom, context=context)
#         return fol_obj.unlink(cr, uid, fol_ids, context=context)
#
#     def copy_data(self, cr, uid, ids, default=None, context=None):
#         """
#         Reset some fields to their initial values
#         """
#         default = default or {}
#         default.update(
#             self.get_fields_to_update(cr, uid, 'activate', context=context))
#         res = super(mozaik_abstract_model, self).copy_data(
#             cr, uid, ids, default=default, context=context)
#         return res
#
    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """
        * Add the "popup" item into the context if the form will be shown as a
          popup
        * Generate a domain on all fields to make the form readonly when
          document is inactive
        * Work around the automatic form generation when it is inherited from
          an other model TODO -> still mandatory (perhaps in another module)
        * Wrongly handle by oe, add manually the readonly attribute to
          message_ids if needed
        """

        # if view_type == 'form':
        #     if not toolbar:
        #         context.update(popup=True)
        #     if uid != SUPERUSER_ID and not context.get('is_developper'):
        #         context.update(add_readonly_condition=True)

        cr = self.env.cr
        if not view_id and not self.env.context.get('%s_view_ref' % view_type):
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

        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        # if view_type == 'form' and not context.get('in_mozaik_user'):
        #     doc = etree.XML(res['arch'])
        #     for node in doc.xpath("//field[@name='message_ids']"):
        #         node.set('readonly', '1')
        #     res['arch'] = etree.tostring(doc)
        return res
#
# # public methods
#
#     @api.cr_uid_ids_context
#     def message_post(self, cr, uid, thread_id, context=None, **kwargs):
#         """
#         Do not auto-subscribe
#         """
#         ctx = dict(context or {}, mail_create_nosubscribe=True)
#         ctx.pop('mail_post_autofollow', None)
#         ctx['is_notification'] = True
#         return super(mozaik_abstract_model, self).message_post(
#             cr, uid, thread_id, context=ctx, **kwargs)
#
#     def get_formview_id(self, cr, uid, _id, context=None):
#         """ Return a view id to open the document with.
#
#             :param int id: id of the document to open
#         """
#         view_ids = self.env['ir.ui.view'].search(
#             cr, uid, [('model', '=', self._name),
#                       ('type', '=', 'form')],
#             limit=1, context=context)
#         return view_ids[0] if view_ids else False
#
#     @api.cr_uid_id_context
#     def display_object_in_form_view(self, cr, uid, object_id, context=None):
#         """
#         Return the object (with given id) in the default form view
#         """
#         return self.get_formview_action(cr, uid, object_id, context=context)
#
#     def get_relation_column_name(self, cr, uid, relation_model, context=None):
#         return self.env['ir.model']._get_relation_column_name(
#             cr, uid, self._name, relation_model, context=context)
#
#
# # Replace the orm.transfer_node_to_modifiers functions.
#
# original_transfer_node_to_modifiers = orm.transfer_node_to_modifiers
# XP = "//field[not(ancestor::div[(@name='dev') or (@name='chat')])]" \
#      "[not(ancestor::field)]"
#
#
# def transfer_node_to_modifiers(node, modifiers, context=None,
#                                in_tree_view=False):
#     '''
#     Add conditions on usefull fields (but chatting fields) to make
#     the form readonly if the document is inactive
#     '''
#     fct_src = original_transfer_node_to_modifiers
#     trace = False
#
#     if context and context.get('add_readonly_condition'):
#         context.pop('add_readonly_condition')
#
#         if trace:
#             # etree.tostring(node)
#             pass
#         if node.xpath("//field[@name='active'][not(ancestor::field)]"):
#             for nd in node.xpath(XP):
#                 if nd.get('readonly', '') == '1':
#                     continue
#                 attrs_str = nd.get('attrs') or '{}'
#                 attrs = eval(attrs_str)
#                 if attrs.get('readonly'):
#                     dom = str(attrs.get('readonly'))
#                     if len(dom.split("'active'")) > 1:
#                         continue
#                 nd.set('aroc', '1')
#
#     aroc = node.get('aroc')
#     if aroc:
#         node.attrib.pop('aroc')
#         aroc = not modifiers.get('readonly', False)
#     if aroc:
#         attrs_str = node.get('attrs') or '{}'
#         attrs = eval(attrs_str)
#         if attrs.get('readonly'):
#             dom = str(attrs.get('readonly'))[1:-1]
#             dom = "['|', ('active', '=', False), %s]" % dom
#             attrs['readonly'] = eval(dom)
#         else:
#             attrs['readonly'] = [('active', '=', False)]
#         attrs = str(attrs)
#         node.set('attrs', attrs)
#         if trace:
#             _logger.warning(
#                 'Field %s - attrs before: %s - after: %s',
#                 node.get('name'), attrs_str, attrs)
#
#     return fct_src(node, modifiers, context=context, in_tree_view=in_tree_view)
#
#
# orm.transfer_node_to_modifiers = transfer_node_to_modifiers
