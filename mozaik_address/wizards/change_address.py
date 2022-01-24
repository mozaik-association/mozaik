# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ChangeAddress(models.TransientModel):

    _name = "change.address"
    _description = "Change the address on a partner"

    address_id = fields.Many2one(comodel_name="address.address", ondelete="cascade")
    partner_ids = fields.Many2many(comodel_name="res.partner", ondelete="cascade")

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

    def doit(self):
        for wizard in self:
            wizard.partner_ids.write(
                {
                    "address_address_id": wizard.address_id,
                }
            )
