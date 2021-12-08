# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    suggested_answer_ids = fields.One2many(
        "survey.question.answer.by.default",
        "question_id",
        string="Types of answers",
        copy=True,
        help="Labels used for proposed choices: "
        "simple choice, multiple choice and columns of matrix",
    )
    matrix_subtype = fields.Selection(
        [("simple", "One choice per row"), ("multiple", "Multiple choices per row")],
        string="Matrix Type",
        default="simple",
    )
    matrix_row_ids = fields.One2many(
        "survey.question.answer.by.default",
        "matrix_question_id",
        string="Matrix Rows",
        copy=True,
        help="Labels used for proposed choices: rows of matrix",
    )

    constr_mandatory = fields.Boolean("Mandatory Answer")
    constr_error_msg = fields.Char(
        "Error message",
        translate=True,
        default=lambda self: _("This question requires an answer."),
    )


class SurveyQuestionAnswerByDefault(models.Model):
    _name = "survey.question.answer.by.default"
    _description = (
        "Template for answers to multiple choice questions "
        "that will be loaded in every new survey."
    )
    _rec_name = "value"

    question_id = fields.Many2one(
        "survey.question.by.default", string="Question", ondelete="cascade"
    )
    matrix_question_id = fields.Many2one(
        "survey.question.by.default",
        string="Question (as matrix row)",
        ondelete="cascade",
    )
    sequence = fields.Integer("Label Sequence order", default=10)
    value = fields.Char("Suggested value", translate=True, required=True)

    @api.constrains("question_id", "matrix_question_id")
    def _check_question_not_empty(self):
        """Ensure that field question_id XOR field matrix_question_id is not null"""
        for label in self:
            if not bool(label.question_id) != bool(label.matrix_question_id):
                raise ValidationError(
                    _("A label must be attached to only one question.")
                )
