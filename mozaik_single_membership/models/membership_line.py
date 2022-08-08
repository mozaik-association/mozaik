# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    previous_state_id = fields.Many2one(
        comodel_name="membership.state", string="Previous State"
    )

    @api.model
    def _update_previous_state(self, vals):
        partner_id = vals.get("partner_id")
        previous_line = self.env["membership.line"].search(
            [("partner_id", "=", partner_id), ("date_to", "!=", False)],
            limit=1,
            order="date_to desc, create_date desc",
        )
        if previous_line:
            vals["previous_state_id"] = previous_line.state_id.id
        else:
            vals["previous_state_id"] = (
                self.env["membership.state"]._get_default_state().id
            )

    @api.model
    def create(self, vals):
        self._update_previous_state(vals)
        return super().create(vals)
