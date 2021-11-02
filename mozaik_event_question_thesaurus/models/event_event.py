# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class EventEvent(models.Model):

    _inherit = "event.event"

    def write(self, vals):
        """We add a check to prevent changing the type of an event
        if there are already attendees."""
        for rec in self:
            if (
                "event_type_id" in vals
                and vals["event_type_id"] != rec.event_type_id.id
                and rec.seats_expected > 0
            ):
                raise ValidationError(
                    _(
                        "You cannot change the type of an event when there are attendees."
                    )
                )
        return super(EventEvent, self).write(vals)

    @api.depends("event_type_id")
    def _compute_question_ids(self):
        super()._compute_question_ids()
        for event in self:
            command = [(5, 0)]
            if event.event_type_id.use_mail_schedule:
                command += [
                    (
                        0,
                        0,
                        {
                            "title": question.title,
                            "question_type": question.question_type,
                            "sequence": question.sequence,
                            "once_per_order": question.once_per_order,
                            "is_mandatory": question.is_mandatory,
                            "interest_ids": question.interest_ids,
                            "answer_ids": [
                                (
                                    0,
                                    0,
                                    {"name": answer.name, "sequence": answer.sequence},
                                )
                                for answer in question.answer_ids
                            ],
                        },
                    )
                    for question in event.event_type_id.question_ids
                ]
            event.write({"question_ids": command})
