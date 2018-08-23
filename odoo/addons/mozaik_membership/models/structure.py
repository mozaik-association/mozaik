# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tools import SUPERUSER_ID
from openerp import fields, api
from openerp.osv import orm

PARTNER_ACTION = 'mozaik_person.natural_res_partner_action'


class sta_assembly(orm.Model):

    _inherit = 'sta.assembly'

    def _pre_update(self, cr, uid, vals, context=None):
        '''
        When instance_id is touched force an update of int_instance_id
        '''
        res = {}
        if 'instance_id' in vals:
            instance_id = vals['instance_id']
            int_instance_id = self.pool['sta.instance'].\
                read(cr, uid, instance_id, ['int_instance_id'],
                     context=context)['int_instance_id']
            if int_instance_id:
                res = {'int_instance_id': int_instance_id[0]}
        return res

    def create(self, cr, uid, vals, context=None):
        '''
        Set the Responsible Internal Instance linked to the result Partner
        '''
        if 'instance_id' in vals:
            vals.update(self._pre_update(cr, uid, vals, context=context))
        res = super(sta_assembly, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        vals.update(self._pre_update(cr, uid, vals, context=context))
        res = super(sta_assembly, self).write(
            cr, uid, ids, vals, context=context)
        return res


class int_instance(orm.Model):

    _inherit = 'int.instance'

    @api.multi
    def _get_member_ids(self):
        partner_obj = self.env['res.partner']
        domain = [
            ('int_instance_id', '=', self.id),
            ('is_company', '=', False)
        ]
        return [partner.id for partner in partner_obj.search(domain)]

    @api.one
    def _compute_member_count(self):
        self.member_count = len(self._get_member_ids())

    member_count = fields.Integer(
        compute='_compute_member_count', type='integer', string='Members')

    @api.multi
    def get_member_action(self):
        self.ensure_one()
        action = PARTNER_ACTION.split('.') or []

        module = action[0]
        action_name = action[1]
        # get model's action to update its domain
        action = self.env['ir.actions.act_window'].for_xml_id(
            module, action_name)

        action['domain'] = [('int_instance_id', '=', self.id)]
        return action

    @api.cr_uid_ids_context
    def check_mail_message_access(
            self, cr, uid, mids, operation, model_obj=None, context=None):
        """
        When user has sufficient rights to create a new instance, it has also
        sufficient rights to create the related notification
        """
        if operation == 'create':
            return
        super(int_instance, self).check_mail_message_access(
            cr, uid, mids, operation, model_obj=model_obj, context=context)

    def create(self, cr, uid, vals, context=None):
        res = super(int_instance, self).create(cr, uid, vals, context=context)
        if not vals.get('parent_id'):
            if uid != SUPERUSER_ID:
                # because the user has rights to create a new instance
                # this new instance has to be added to users's internal
                # instances if it is a root instance
                u = self.pool['res.users'].browse(
                    cr, SUPERUSER_ID, uid, context=context)
                u.partner_id.write({'int_instance_m2m_ids': [(4, res)]})
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(int_instance, self).write(
            cr, uid, ids, vals, context=context)
        if 'partner_id' in vals:
            self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def unlink(self, cr, uid, ids, context=None):
        res = super(int_instance, self).unlink(cr, uid, ids, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def get_default(self, cr, uid, context=None):
        """
        Returns the default Internal Instance
        """
        res = [super(int_instance, self).get_default(cr, uid, context=context)]
        if res:
            res = self.search(cr, uid, [('id', 'in', res)], context=context)
        if not res:
            res = self.pool['res.users'].internal_instances(cr, uid)
        return res and res[0] or False


class int_assembly(orm.Model):

    _inherit = 'int.assembly'

    def create(self, cr, uid, vals, context=None):
        '''
        Responsible Internal Instance linked to the result Partner is the
        Instance of the Assembly
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(int_assembly, self).create(cr, uid, vals, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(int_assembly, self).write(
            cr, uid, ids, vals, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def unlink(self, cr, uid, ids, context=None):
        res = super(int_assembly, self).unlink(cr, uid, ids, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res


class ext_assembly(orm.Model):

    _inherit = 'ext.assembly'

    def create(self, cr, uid, vals, context=None):
        '''
        Responsible Internal Instance linked to the result Partner is
        the Instance of the Assembly
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(ext_assembly, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(ext_assembly, self).write(cr, uid, ids, vals,
                                              context=context)
        return res
