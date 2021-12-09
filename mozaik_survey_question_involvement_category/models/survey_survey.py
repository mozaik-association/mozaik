# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    def _get_answer_copy_values(self, question, answer):
        dict = super()._get_answer_copy_values(question, answer)
        dict.update({"involvement_category_id": answer.involvement_category_id.id})
        return dict
