# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    is_private = fields.Boolean(
        string="Is private",
        help="If ticked, only members of authorized internal "
        "instances have access to the survey and its answers.",
        default=False,
    )

    int_instance_id = fields.Many2one(
        "int.instance",
        string="Internal instance",
        help="Internal instance of the survey",
        default=lambda self: self.env.user.partner_id.int_instance_id,
    )
