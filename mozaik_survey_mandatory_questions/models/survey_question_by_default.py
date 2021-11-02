# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class SurveyQuestionByDefault(models.Model):

    _name = "survey.question.by.default"
    _description = "Template for questions that will be loaded in every new survey."
    _rec_name = "title"

    title = fields.Char("Title", required=True, translate=True)
    question_type = fields.Selection(
        [
            ("text_box", "Multiple Lines Text Box"),
            ("char_box", "Single Line Text Box"),
            ("numerical_box", "Numerical Value"),
            ("date", "Date"),
            ("datetime", "Datetime"),
            ("simple_choice", "Multiple choice: only one answer"),
            ("multiple_choice", "Multiple choice: multiple answers allowed"),
            ("matrix", "Matrix"),
        ],
        string="Question Type",
        default="text_box",
        readonly=False,
        store=True,
        required=True,
    )
    constr_mandatory = fields.Boolean("Mandatory Answer")
    constr_error_msg = fields.Char(
        "Error message",
        translate=True,
        default=lambda self: _("This question requires an answer."),
    )
