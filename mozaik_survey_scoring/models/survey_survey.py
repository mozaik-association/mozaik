# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    exclude_not_answered_from_total = fields.Boolean(
        "Exclude Not Answered Questions from Total",
        help="If ticked, the questions without an answer "
        "will not be used to compute the total score.",
    )
