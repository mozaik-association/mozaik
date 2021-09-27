# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StaAssembly(models.Model):

    _inherit = 'sta.assembly'

    @api.model
    def create(self, vals):
        '''
        Set the Responsible Internal Instance linked to the result Partner
        '''
        self._sanitize_instance(vals)
        res = super().create(vals)
        return res

    def write(self, vals):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        self._sanitize_instance(vals)
        res = super().write(vals)
        return res

    @api.model
    def _sanitize_instance(self, vals):
        '''
        Link result Partner to the Internal Instance of the state instance
        '''
        if 'instance_id' in vals:
            instance_id = vals['instance_id']
            int_instance_id = self.env['sta.instance'].browse(instance_id)\
                .int_instance_id
            vals.update({'force_int_instance_id': int_instance_id.id})
