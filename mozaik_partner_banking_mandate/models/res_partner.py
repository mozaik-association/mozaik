# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    has_valid_mandate = fields.Boolean(
        string="Has Valid Mandate", compute="_compute_has_valid_mandate", store=True
    )

    def _compute_has_valid_mandate(self):
        mandate_data = self.env["account.banking.mandate"].read_group(
            [("partner_id", "in", self.ids), ("state", "=", "valid")],
            ["partner_id"],
            ["partner_id"],
        )
        mapped_data = {
            mandate["partner_id"][0]: mandate["partner_id_count"]
            for mandate in mandate_data
        }
        for partner in self:
            partner.has_valid_mandate = mapped_data.get(partner.id, False)
