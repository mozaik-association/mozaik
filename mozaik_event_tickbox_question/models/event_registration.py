# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventRegistration(models.Model):

    _inherit = "event.registration"

    @api.constrains("registration_answer_ids")
    def _check_value_tickbox(self):
        """
        We have to search, in the questions associated to the event, if
        there are mandatory tickbox questions. Every such question have
        to be present in the partner registration form.
        We search by title (we thus assume that in a given event, two questions
        never have the same title).
        """
        for record in self:
            mandatory_question_titles = self.event_id.question_ids.filtered(
                lambda qu: qu.question_type == "tickbox" and qu.is_mandatory
            ).mapped("title")
            answer_titles = record.registration_answer_ids.mapped("question_id.title")
            if not set(mandatory_question_titles).issubset(set(answer_titles)):
                raise ValidationError(
                    _("The partner didn't answer to all mandatory tickbox questions.")
                )

    def _get_involvement_and_interests(self):
        """
        Getting involvement and interests from tickbox questions:
        If the tickbox question is ticked, add the involvement
        """
        command_ic, command_interests = super()._get_involvement_and_interests()

        for answer in self.registration_answer_ids.filtered(
            lambda r: r.question_type == "tickbox" and r.value_tickbox
        ):
            if answer.question_id.involvement_category_id:
                command_ic += [(4, answer.question_id.involvement_category_id.id)]
                command_interests += [
                    (4, interest.id)
                    for interest in answer.question_id.involvement_category_id.interest_ids
                ]

        return command_ic, command_interests


class EventRegistrationAnswer(models.Model):

    _inherit = "event.registration.answer"
    is_mandatory = fields.Boolean(related="question_id.is_mandatory")
    value_tickbox = fields.Boolean(string="Checked", default=False)

    _sql_constraints = [
        (
            "value_check",
            "CHECK(value_tickbox IS NOT NULL OR "
            "value_answer_id IS NOT NULL OR "
            "COALESCE(value_text_box, '') <> '')",
            "There must be a suggested value or a text value.",
        )
    ]

    @api.constrains("value_tickbox")
    def _check_value_tickbox(self):
        for record in self:
            if record.is_mandatory and not record.value_tickbox:
                raise ValidationError(
                    _("At least one mandatory tickbox is not checked.")
                )
