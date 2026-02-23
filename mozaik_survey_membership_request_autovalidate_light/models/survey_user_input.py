# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.membership_request_id.autovalidation_type = (
            res.survey_id.autovalidation_type
        )
        return res
