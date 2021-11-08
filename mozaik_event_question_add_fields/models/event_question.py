# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EventQuestion(models.Model):

    _inherit = "event.question"

    def adding_new_question_to_event(self):
        """
        Returns a dictionary of fields (along with their value) to copy
        when loading a question from an event type to an event.
        """
        self.ensure_one()
        return {
            "title": self.title,
            "question_type": self.question_type,
            "sequence": self.sequence,
            "once_per_order": self.once_per_order,
            "answer_ids": [
                (
                    0,
                    0,
                    {"name": answer.name, "sequence": answer.sequence},
                )
                for answer in self.answer_ids
            ],
        }
