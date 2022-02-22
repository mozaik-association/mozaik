# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    domain = fields.Text(
        string="Target partners domain",
        help="Add a domain on partners model to limit the access of this petition.",
        default="[]",
    )
