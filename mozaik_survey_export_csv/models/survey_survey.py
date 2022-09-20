# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    def export_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "survey.export",
            "view_mode": "form",
            "target": "new",
            "context": {"default_survey_id": self.id},
        }
