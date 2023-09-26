# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_donor = fields.Boolean(
        string="Is a donor",
        compute="_compute_is_donor",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "partner_involvement_ids",
        "partner_involvement_ids.active",
        "partner_involvement_ids.involvement_type",
    )
    def _compute_is_donor(self):
        for partner in self:
            types = partner.partner_involvement_ids.mapped("involvement_type")
            partner.is_donor = "donation" in types
