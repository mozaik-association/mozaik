# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CreateCoResidencyAddress(models.TransientModel):

    _name = "create.co.residency.address"
    _description = "Create Co-Residency Address Wizard"

    partner_ids = fields.Many2many("res.partner", readonly=True)
    line = fields.Char("Line 1")
    line2 = fields.Char("Line 2")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ids = (
            self.env.context.get("active_ids")
            or (
                self.env.context.get("active_id")
                and [self.env.context.get("active_id")]
            )
            or []
        )
        if "partner_ids" in fields_list:
            res["partner_ids"] = ids
        return res

    @api.onchange("partner_ids")
    def _onchange_partners_address(self):
        for w in self:
            co_residency = w.partner_ids.mapped("co_residency_id")
            if co_residency:
                w.line = co_residency.line
                w.line2 = co_residency.line2

    def create_co_residency(self):
        for w in self:
            co_residency = w.partner_ids.mapped("co_residency_id")
            if not co_residency:
                co_residency = self.env["co.residency"].create(
                    {
                        "line": w.line,
                        "line2": w.line2,
                    }
                )
            else:
                co_residency.write(
                    {
                        "line": w.line,
                        "line2": w.line2,
                    }
                )
            w.partner_ids.write(
                {
                    "co_residency_id": co_residency.id,
                }
            )
