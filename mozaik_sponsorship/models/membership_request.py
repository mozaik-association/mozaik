# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    can_be_sponsored = fields.Boolean(compute="_compute_can_be_sponsored")
    sponsor_id = fields.Many2one("res.partner")

    @api.depends("partner_id", "partner_id.membership_state_id")
    def _compute_can_be_sponsored(self):
        """
        Partner can NOT be sponsored if:
        * he's a member or (former) member committee
        * he's a former member (or former member break,...) and already has a sponsor

        He can be sponsored in all other cases (including if he's a new contact)
        """
        self.can_be_sponsored = True
        for mr in self.filtered("partner_id"):
            partner = mr.partner_id
            if partner.membership_state_id.code in [
                "member",
                "member_committee",
                "former_member_committee",
            ]:
                mr.can_be_sponsored = False
            elif (
                partner.membership_state_id.code
                in [
                    "former_member",
                    "expulsion_former_member",
                    "resignation_former_member",
                    "inappropriate_former_member",
                    "break_former_member",
                ]
                and partner.sponsor_id
            ):
                mr.can_be_sponsored = False

    def validate_request(self):
        """
        Write the sponsor on the partner
        """
        res = super().validate_request()
        for mr in self.filtered(
            lambda mr: mr.partner_id and mr.can_be_sponsored and mr.sponsor_id
        ):
            mr.partner_id.sponsor_id = mr.sponsor_id
        return res
