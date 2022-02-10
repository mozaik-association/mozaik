# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    is_private = fields.Boolean(
        string="Is private",
        help="If ticked, only members of authorized internal "
        "instances have access to the survey.",
        default=False,
        tracking=True,
    )
    int_instance_ids = fields.Many2many(
        "int.instance",
        string="Internal instances",
        help="Internal instances of the survey",
        default=lambda self: self.env.user.int_instance_m2m_ids,
        tracking=True,
    )
