# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveyQuestion(models.Model):

    _inherit = "survey.question"

    bridge_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Bridge field",
        default=False,
        help="The answer to this question will fill a field from the membership request.",
        ondelete="cascade",
    )
