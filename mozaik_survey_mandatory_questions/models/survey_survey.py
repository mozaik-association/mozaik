# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    question_and_page_ids = fields.One2many(
        default=lambda self: self._load_questions_by_default()
    )

    def _get_matrix_row_copy_values(self, question, answer):
        """
        Returns a dictionary of fields (along with their value) to copy
        when loading the rows of a matrix question by default in a survey.
        """
        return {
            "value": answer.value,
            "sequence": answer.sequence,
            "matrix_question_id": question.id,
        }

    def _get_answer_copy_values(self, question, answer):
        """
        Returns a dictionary of fields (along with their value) to copy
        when loading the answer to a question by default in a survey.
        """
        return {
            "value": answer.value,
            "sequence": answer.sequence,
            "question_id": question.id,
        }

    def _get_question_copy_values(self, question):
        """
        Returns a dictionary of fields (along with their value) to copy
        when loading a question by default in a survey.
        """
        question.ensure_one()

        suggested_answer_ids = []
        for answer in question.suggested_answer_ids:
            suggested_answer_ids += [
                (
                    0,
                    0,
                    self._get_answer_copy_values(question, answer),
                )
            ]
        matrix_row_ids = []
        for answer in question.matrix_row_ids:
            matrix_row_ids += [
                (
                    0,
                    0,
                    self._get_matrix_row_copy_values(question, answer),
                )
            ]

        return {
            "title": question.title,
            "question_type": question.question_type,
            "matrix_subtype": question.matrix_subtype,
            "constr_mandatory": question.constr_mandatory,
            "constr_error_msg": question.constr_error_msg,
            "suggested_answer_ids": suggested_answer_ids,
            "matrix_row_ids": matrix_row_ids,
        }

    def _load_questions_by_default(self):
        command = []
        for question in self.env["survey.question.by.default"].search([]):
            command += [(0, 0, self._get_question_copy_values(question))]
        return command
