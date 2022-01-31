# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    unemployed_change = fields.Selection(
        [
            ("force_true", "Set as unemployed"),
            ("force_false", "Set as employed"),
        ],
        string="Employed / Unemployed",
        default=False,
    )

    def validate_request(self):
        res = super().validate_request()
        for mr in self:
            if mr.unemployed_change == "force_true" and mr.partner_id:
                mr.partner_id.unemployed = True
            elif mr.unemployed_change == "force_false" and mr.partner_id:
                mr.partner_id.unemployed = False
        return res
