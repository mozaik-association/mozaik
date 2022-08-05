# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import first


class MembershipLine(models.Model):

    _inherit = "membership.line"

    previous_state_id = fields.Many2one(
        comodel_name="membership.state", string="Previous State"
    )

    def _update_previous_state(self):
        self.ensure_one()
        partner = self.partner_id
        previous_line = first(
            self.env["membership.line"].search(
                [("partner_id", "=", partner.id), ("date_to", "!=", False)],
                order="date_to desc, create_date desc",
            )
        )
        if previous_line:
            self.previous_state_id = previous_line.state_id
        else:
            self.previous_state_id = self.env["membership.state"]._get_default_state()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._update_previous_state()
        return res
