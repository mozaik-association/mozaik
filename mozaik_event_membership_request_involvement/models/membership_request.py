# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    event_registration_id = fields.Many2one(
        comodel_name="event.registration",
        string="Associated Event Registration",
        help="The membership request came from an event registration.",
        readonly=True,
    )

    @api.depends("event_registration_id")
    def _compute_force_autoval(self):
        super()._compute_force_autoval()
        for record in self:
            if record.event_registration_id:
                record.force_autoval = record.event_registration_id.force_autoval

    def validate_request(self):
        """
        If the membership request is coming from an event registration
        and if the partner on the event registration is not mentioned,
        then we associate the partner from the membership request
        to the event registration:
        we set the partner into the field "associated_partner_id", if
        not present yet.
        """
        super().validate_request()
        if (
            self.event_registration_id
            and self.state == "validate"
            and self.partner_id
            and not self.event_registration_id.associated_partner_id
        ):
            self.event_registration_id.associated_partner_id = self.partner_id
