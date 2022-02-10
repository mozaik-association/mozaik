# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    is_private = fields.Boolean(related="survey_id.is_private")

    int_instance_ids = fields.Many2many(related="survey_id.int_instance_ids")


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    is_private = fields.Boolean(related="survey_id.is_private")

    int_instance_ids = fields.Many2many(related="survey_id.int_instance_ids")
