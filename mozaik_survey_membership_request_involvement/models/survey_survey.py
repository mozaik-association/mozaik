# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SurveySurvey(models.Model):

    _inherit = "survey.survey"

    def _get_question_copy_values(self, question):
        dic = super()._get_question_copy_values(question)
        dic.update({"bridge_field_id": question.bridge_field_id.id})
        return dic
