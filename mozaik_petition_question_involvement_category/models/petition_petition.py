# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PetitionPetition(models.Model):

    _inherit = "petition.petition"

    def _get_question_copy_values(self, question):
        res = super(PetitionPetition, self)._get_question_copy_values(question)
        answer_ids = [
            (
                0,
                0,
                {
                    "name": answer.name,
                    "sequence": answer.sequence,
                    "interest_ids": answer.interest_ids,
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
