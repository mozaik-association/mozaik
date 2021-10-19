# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class EventEvent(models.Model):

    _inherit = "event.event"

    @api.depends("event_type_id")
    def _compute_question_ids(self):
        """Update event questions from its event type. Depends are set only on
        event_type_id itself to emulate an onchange. Changing event type content
        itself should not trigger this method.

        When synchronizing questions:

          * lines that no answer are removed;
          * type lines are added;
        """
        super()._compute_question_ids()

        for event in self:
            # removing tickbox questions that were added in super()
            # method without adding field is_mandatory
            tickbox_questions = event.question_ids.filtered(
                lambda question: question.question_type == "tickbox"
            )
            command = [(3, question.id) for question in tickbox_questions]

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
                    for question in event.event_type_id.question_ids.filtered(
                        lambda question: question.question_type == "tickbox"
                    )
                ]
            event.question_ids = command
        return self.question_ids
