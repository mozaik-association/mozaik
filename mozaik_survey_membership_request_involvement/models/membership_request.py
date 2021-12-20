# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    survey_user_input_id = fields.Many2one(
        comodel_name="survey.user_input",
        string="Associated Survey Answer",
        help="The membership request came from the answer to a survey.",
        readonly=True,
    )
