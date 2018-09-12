# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class AbstractCoordinate(models.AbstractModel):

    _inherit = ['abstract.coordinate']

    partner_kind = fields.Selection(
        related='partner_id.kind', store=True)
    partner_instance_id = fields.Many2one(
        related='partner_id.int_instance_id',
        string='Partner Internal Instance',
        index=True, readonly=True, store=True)

    @api.multi
    def _update_followers(self):
        """
        Update followers list for each coordinate of the same partner
        """
        for coord in self:
            fol = coord.partner_instance_id._get_instance_followers()
            coord.message_subscribe(fol.ids)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._update_followers()
        return res
