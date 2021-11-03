# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveyQuestion(models.Model):

    _inherit = "survey.question"

    is_private = fields.Boolean(related="survey_id.is_private")

    int_instance_id = fields.Many2one(related="survey_id.int_instance_id")


class SurveyQuestionAnswer(models.Model):
    _inherit = "survey.question.answer"

    is_private = fields.Boolean(related="question_id.is_private")

    int_instance_id = fields.Many2one(related="question_id.int_instance_id")
