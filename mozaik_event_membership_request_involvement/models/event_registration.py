# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EventRegistration(models.Model):

    _inherit = "event.registration"

    associated_partner_id = fields.Many2one(
        "res.partner",
        string="Registered Partner",
        help="Id of the partner that will be associated to the membership request",
    )

    @api.onchange("associated_partner_id")
    def _onchange_associated_partner_id(self):
        """We want, when changing associated_partner_id, the same behavior
        we had when changing partner_id ("Booked by").
        Hence we call the same function
        """
        for registration in self:
            if registration.associated_partner_id:
                registration.update(
                    registration._synchronize_partner_values(
                        registration.associated_partner_id,
                        fnames=["lastname", "firstname", "email", "phone", "mobile"],
                    )
                )

    @api.model
    def create(self, vals):
        registered_partner = False
        if "associated_partner_id" in vals:
            registered_partner = vals["associated_partner_id"]
        rec = super().create(vals)
        rec.with_context(
            {"mr_partner_id": registered_partner}
        )._create_membership_request_from_registration(vals)
        return rec

    def _create_membership_request_from_registration(self, vals):
        self.ensure_one()

        request = self.env["membership.request"]._create_membership_request(vals)
        if request:
            request.write({"event_registration_id": self.id})
            self._add_involvements_to_membership_request(request)
            request._auto_validate(self.event_id.auto_accept_membership)

    def _add_involvements_to_membership_request(self, request):
        """
        Adds to the membership request:
        # 1 the involvement category of the event itself, if set
        # 2 for select questions: all involvement categories
            set on answers that were chosen by the attendee
        # 3 for other types of questions where an involvement category
            is set on the question itself
            (neither select questions, nor text input questions): the involvement category
        For every involvement category added, adds the corresponding interests
          on the membership request.
        """
        self.ensure_one()
        command_ic = []
        command_interests = []
        # 1
        if self.event_id.involvement_category_id:
            command_ic += [(4, self.event_id.involvement_category_id.id)]
            command_interests += [
                (4, interest.id)
                for interest in self.event_id.involvement_category_id.interest_ids
            ]

        # 2
        for answer in self.registration_answer_ids.mapped("value_answer_id").filtered(
            lambda s: s and s.involvement_category_id
        ):
            command_ic += [(4, answer.involvement_category_id.id)]
            command_interests += [
                (4, interest.id)
                for interest in answer.involvement_category_id.interest_ids
            ]

        # 3
        for question in self.registration_answer_ids.question_id.filtered(
            lambda s: s.involvement_category_id
        ):
            command_ic += [(4, question.involvement_category_id.id)]
            command_interests += [
                (4, interest.id)
                for interest in question.involvement_category_id.interest_ids
            ]

        command_ic = list(set(command_ic))  # removing duplicates
        command_interests = list(set(command_interests))
        request.write(
            {"involvement_category_ids": command_ic, "interest_ids": command_interests}
        )
