# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    def _validate_request_involvement(self, mr, partner):
        """
        For involvement categories that correspond to an event,
        we add involvements for answered questions
        """
        super()._validate_request_involvement(mr, partner)

        for ic in mr.involvement_category_ids.filtered(
            lambda inv: inv.involvement_type == "event"
        ):
            # Looking for the event.registration whose
            # associated partner is partner
            domain = [
                ("event_id", "=", ic.event_id.id),
                ("lastname", "=", partner.lastname),
                ("firstname", "=", partner.firstname),
                ("email", "=", partner.email),
            ]
            registration = self.env["event.registration"].search(domain)
            if len(registration) != 1:
                raise Exception(
                    _("Cannot find the associated registration to the event.")
                )
            # Which type of exception to raise?
            registration = registration[0]
            for answer in registration.registration_answer_ids:
                # create the associated involvement
                values = {
                    "partner_id": partner.id,
                    "effective_time": mr.effective_time,
                    "involvement_category_id": ic.id,
                    "question_event_id": answer.question_id.id,
                }
                self.env["partner.involvement"].create(values)
