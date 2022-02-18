# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class PetitionRegistration(models.Model):

    _inherit = "petition.registration"

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._create_membership_request_from_registration(vals)
        return rec

    def _create_membership_request_from_registration(self, vals):
        self.ensure_one()

        request = self.env["membership.request"]._create_membership_request(vals)
        if request:
            request.write({"petition_registration_id": self.id})
            self._add_involvements_to_membership_request(request)
            failure_reason = request._auto_validate(
                self.petition_id.auto_accept_membership
            )
            force_autoval = self._context.get("force_autoval", False)

            if failure_reason:
                request._create_note(
                    _("Autovalidation failed"),
                    _("Autovalidation failed. Reason of failure: %s") % failure_reason,
                )

                if force_autoval:
                    request.validate_request()
                    if request.state == "validate":
                        request._create_note(
                            _("Forcing autovalidation"), _("Autovalidation was forced")
                        )
                        partner = request.partner_id
                        if partner:
                            partner._schedule_activity_force_autoval(failure_reason)

    def _add_involvements_to_membership_request(self, request):
        """
        Adds to the membership request:
        # 1 the involvement category of the petition itself, if set
        # 2 for select questions: all involvement categories
            set on answers that were chosen by the signatory
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
        if self.petition_id.involvement_category_id:
            command_ic += [(4, self.petition_id.involvement_category_id.id)]
            command_interests += [
                (4, interest.id)
                for interest in self.petition_id.involvement_category_id.interest_ids
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
