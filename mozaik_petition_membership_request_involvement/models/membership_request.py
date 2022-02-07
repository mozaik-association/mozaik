# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    petition_registration_id = fields.Many2one(
        comodel_name="petition.registration",
        string="Associated Petition Signatory",
        help="The membership request came from a petition signature.",
        readonly=True,
    )

    def validate_request(self):
        """
        If the membership request is coming from a petition registration
        and if the partner on the petition registration is not mentioned,
        then we associate the partner from the membership request
        to the petition registration.
        """
        super().validate_request()
        if (
            self.petition_registration_id
            and self.state == "validate"
            and self.partner_id
            and not self.petition_registration_id.partner_id
        ):
            self.petition_registration_id.partner_id = self.partner_id
