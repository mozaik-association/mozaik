# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, SUPERUSER_ID
from odoo.fields import first
from odoo.tools.safe_eval import safe_eval


class StaAssembly(models.Model):

    _inherit = 'sta.assembly'

    @api.model
    def _pre_update(self, vals):
        '''
        When instance_id is touched force an update of int_instance_id
        '''
        res = {}
        if 'instance_id' in vals:
            instance_id = vals['instance_id']
            int_instance_id = self.env['sta.instance'].browse(instance_id)\
                .int_instance_id
            if int_instance_id:
                res = {'int_instance_id': int_instance_id.id}
        return res

    @api.model
    def create(self, vals):
        '''
        Set the Responsible Internal Instance linked to the result Partner
        '''
        vals.update(self._pre_update(vals))
        res = super().create(vals)
        return res

    @api.multi
    def write(self, vals):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        vals.update(self._pre_update(vals))
        res = super().write(vals)
        return res


class IntInstance(models.Model):

    _inherit = 'int.instance'

    member_count = fields.Integer(
        compute='_compute_member_count', string='Members')
    partner_ids = fields.One2many(
        comodel_name="res.partner", inverse_name="int_instance_id")
    partner_m2m_ids = fields.Many2many(
        comodel_name="res.partner")

    @api.multi
    def _get_member_ids(self):
        self.ensure_one()
        partner_obj = self.env['res.partner']
        domain = [
            ('int_instance_id', '=', self.id),
            ('is_company', '=', False)
        ]
        return partner_obj.search(domain)

    @api.multi
    @api.depends("partner_ids")
    def _compute_member_count(self):
        for inst in self:
            inst.member_count = len(inst._get_member_ids())

    @api.multi
    def get_member_action(self):
        self.ensure_one()
        action = self.env.ref(
            "mozaik_person.res_partner_natural_person_action").read()[0]
        domain = safe_eval(action['domain'])
        action['domain'] = domain + [('int_instance_id', '=', self.id)]
        return action

    @api.model
    def check_mail_message_access(self, res_ids, operation, model_name=None):
        """
        When user has sufficient rights to create a new instance, it has also
        sufficient rights to create the related notification
        """
        if operation == 'create':
            return
        super().check_mail_message_access(operation)

    @api.model
    def create(self, vals):
        if not vals.get('parent_id'):
            if self.env.uid != SUPERUSER_ID:
                # because the user has rights to create a new instance
                # this new instance has to be added to users's internal
                # instances if it is a root instance
                u = self.env.user
                vals["partner_m2m_ids"] = [(4, u.partner_id.id)]
        res = super().create(vals)
        return res

    @api.model
    def _get_default_int_instance(self):
        """
        Returns the default Internal Instance
        """
        res = super()._get_default_int_instance()
        if not res:
            res = self.pool['res.users']._internal_instances()
        return first(res)


class IntAssembly(models.Model):

    _inherit = 'int.assembly'

    @api.model
    def create(self, vals):
        '''
        Responsible Internal Instance linked to the result Partner is the
        Instance of the Assembly
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super().create(vals)
        return res

    @api.multi
    def write(self, vals):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super().write(vals)
        return res


class ExtAssembly(models.Model):

    _inherit = 'ext.assembly'

    @api.model
    def create(self, vals):
        '''
        Responsible Internal Instance linked to the result Partner is
        the Instance of the Assembly
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super().create(vals)
        return res

    @api.multi
    def write(self, vals):
        """
        Update the Responsible Internal Instance linked to the result Partner
        """
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super().write(vals)
        return res
