# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveyQuestionAnswer(models.Model):

    _inherit = "survey.question.answer"

    involvement_category_id = fields.Many2one(
        "partner.involvement.category", string="Involvement Category"
    )
