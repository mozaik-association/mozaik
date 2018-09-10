# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AssemblyMixin(models.AbstractModel):

    _name = 'assembly.mixin'

    @api.model
    def create(self, vals):
        self._sanitize_instance(vals)
        res = super().create(vals)
        return res

    @api.multi
    def write(self, vals):
        self._sanitize_instance(vals)
        res = super().write(vals)
        return res

    @api.model
    def _sanitize_instance(self, vals):
        '''
        Responsible Internal Instance linked to the result Partner is the
        Instance of the Assembly
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
