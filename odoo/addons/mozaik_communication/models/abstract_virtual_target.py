# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AbstractVirtualTarget(models.AbstractModel):
    """
    Abstract model used to contain common properties for virtual models
    """
    _name = 'abstract.virtual.target'
    _description = 'Abstract Virtual Target'

    @api.multi
    def get_partner_action(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.partner_id.id,
            'target': 'current',
        }
