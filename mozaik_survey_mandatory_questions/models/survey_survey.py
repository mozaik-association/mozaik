# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    question_and_page_ids = fields.One2many(
        default=lambda self: self._get_personal_questions()
    )

    def _get_personal_questions(self):
        command = [
            (
                0,
                0,
                {
                    "title": "Personal information",
                    "is_page": True,
                },
            ),
            (
                0,
                0,
                {
                    "title": "Please enter your firstname",
                    "is_page": False,
                    "question_type": "char_box",
                    "constr_mandatory": True,
                },
            ),
            (
                0,
                0,
                {
                    "title": "Please enter your lastname",
                    "is_page": False,
                    "question_type": "char_box",
                    "constr_mandatory": True,
                },
            ),
            (
                0,
                0,
                {
                    "title": "Please enter your email",
                    "is_page": False,
                    "question_type": "char_box",
                    "constr_mandatory": True,
                },
            ),
            (
                0,
                0,
                {
                    "title": "Please enter your phone number",
                    "is_page": False,
                    "question_type": "char_box",
                },
            ),
        ]
        return command
