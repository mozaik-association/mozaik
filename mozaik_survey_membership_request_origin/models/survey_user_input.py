# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        survey_origin = self.env.ref(
            "mozaik_survey_membership_request_origin.membership_request_origin_survey"
        )
        res.mapped("membership_request_id").write({"origin_id": survey_origin.id})
        return res
