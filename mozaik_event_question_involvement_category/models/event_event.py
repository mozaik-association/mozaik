# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EventEvent(models.Model):

    _inherit = "event.event"

    def _get_question_copy_values(self, question):
        res = super(EventEvent, self)._get_question_copy_values(question)
        answer_ids = [
            (
                0,
                0,
                {
                    "name": answer.name,
                    "sequence": answer.sequence,
                    "involvement_category_id": answer.involvement_category_id,
                },
            )
            for answer in question.answer_ids
        ]
        res.update(
            {
                "answer_ids": answer_ids,
                "involvement_category_id": question.involvement_category_id,
            }
        )
        return res
