# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


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
