# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ForceIntInstance(models.TransientModel):

    _name = 'force.int.instance'
    _description = 'Change Internal Instance'

    int_instance_id = fields.Many2one(
        'int.instance', string='Internal Instance',
        required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner',
        default=lambda s: s._default_partner_id())

    def _default_partner_id(self):
        return self.env.context.get('active_id', False)

    def force_int_instance_action(self):
        '''
        update partner internal instance
        '''
        for wiz in self:
            if wiz.int_instance_id != wiz.partner_id.int_instance_id:
                partner_id = wiz.partner_id
                partner_id._change_instance(wiz.int_instance_id)

        return True
