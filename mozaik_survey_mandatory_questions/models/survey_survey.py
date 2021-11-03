# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    question_and_page_ids = fields.One2many(
        default=lambda self: self._load_questions_by_default()
    )

    def _load_questions_by_default(self):
        command = [
            (
                0,
                0,
                {
                    "title": question.title,
                    "question_type": question.question_type,
                    "constr_mandatory": question.constr_mandatory,
                    "constr_error_msg": question.constr_error_msg,
                },
            )
            for question in self.env["survey.question.by.default"].search([])
        ]
        return command
