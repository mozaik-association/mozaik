# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    disabled_change = fields.Selection(
        [
            ("force_true", "Set as disabled"),
            ("force_false", "Not disabled anymore"),
        ],
        string="Disabled / Not disabled",
        default=False,
    )

    def validate_request(self):
        res = super().validate_request()
        for mr in self:
            if mr.disabled_change == "force_true" and mr.partner_id:
                mr.partner_id.disabled = True
            elif mr.disabled_change == "force_false" and mr.partner_id:
                mr.partner_id.disabled = False
        return res
