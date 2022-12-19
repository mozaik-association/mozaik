# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ChangeAddress(models.TransientModel):

    _name = "change.address"
    _description = "Change the address on a partner"

    address_id = fields.Many2one(comodel_name="address.address", ondelete="cascade")
    partner_ids = fields.Many2many(comodel_name="res.partner", ondelete="cascade")
    move_co_residency = fields.Boolean(
        help="Move all partners that are in the same co-residencies. "
        "Pay attention: do not move partners that are not into a co-residency."
    )
    have_co_residency = fields.Boolean(compute="_compute_have_co_residency")

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
        if "have_co_residency" in fields_list:
            partners = self.env["res.partner"].browse(ids)
            res["have_co_residency"] = bool(partners.mapped("co_residency_id"))
        return res

    @api.depends("partner_ids", "partner_ids.co_residency_id")
    def _compute_have_co_residency(self):
        for w in self:
            w.have_co_residency = bool(w.partner_ids.mapped("co_residency_id"))

    def doit(self):
        for wizard in self:
            vals = {
                "address_address_id": wizard.address_id.id,
            }
            if wizard.move_co_residency:
                partners_by_co_residency = {}
                for co_residency in wizard.partner_ids.mapped("co_residency_id"):
                    partners_by_co_residency[co_residency] = co_residency.partner_ids
                wizard.partner_ids = wizard.partner_ids.mapped(
                    "co_residency_id.partner_ids"
                )
            else:
                vals["co_residency_id"] = False
            wizard.partner_ids.write(vals)
            if wizard.move_co_residency:
                # in some case, the co-residency can be dropped because of the duplicate
                # we make sure that it still have a co-residency if needed
                for co_residency, partners in partners_by_co_residency.items():
                    partners.write(
                        {
                            "co_residency_id": co_residency.id,
                        }
                    )
