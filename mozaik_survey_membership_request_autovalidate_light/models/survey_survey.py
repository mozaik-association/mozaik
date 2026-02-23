# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    autovalidation_type = fields.Selection(
        [("light", "Light"), ("complete", "Complete")], default="complete"
    )
