# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ChangeInstance(models.TransientModel):

    _name = "change.instance"
    _description = "Change instance"

    instance_id = fields.Many2one(comodel_name="int.instance", ondelete="cascade")
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
            for partner in wizard.partner_ids:
                if wizard.instance_id not in partner.int_instance_ids:
                    if partner.membership_line_ids:
                        state = partner.membership_state_id
                        active_memberships = partner.membership_line_ids.filtered(
                            lambda s: s.active
                        )
                        active_memberships._close(force=True)
                        active_memberships.flush()
                        w = self.env["add.membership"].create(
                            {
                                "int_instance_id": wizard.instance_id.id,
                                "partner_id": partner.id,
                                "product_id": active_memberships.product_id.id,
                                "state_id": state.id,
                                "price": active_memberships.price
                                if not active_memberships.paid
                                else 0,
                            }
                        )
                        w.action_add()
                    else:
                        partner.force_int_instance_id = wizard.instance_id
