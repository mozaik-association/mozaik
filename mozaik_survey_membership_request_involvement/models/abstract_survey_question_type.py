# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AbstractSurveyQuestionType(models.AbstractModel):

    _name = "abstract.survey.question.type"
    _description = "Abstract Survey Question Type"

    def _get_dic(self):
        """Returns a dictionary of possible types of answers for questions linked
        to a field from membership.request"""
        return {
            "text_box": ["text"],
            "char_box": ["char"],
            "numerical_box": ["integer", "float"],
            "date": ["date"],
            "datetime": ["datetime"],
        }

    def _get_expected_type_of_answer(self, question):
        """
        question is either a survey.question or a survey.question.by.default
        Returns ttypes that are compatible with question.bridge_field
        """
        dic = self._get_dic()
        return dic[question.question_type]
