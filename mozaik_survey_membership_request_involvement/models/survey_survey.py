# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SurveySurvey(models.Model):

    _name = "survey.survey"
    _inherit = ["survey.survey", "abstract.survey.question.type"]

    def _get_question_copy_values(self, question):
        dic = super()._get_question_copy_values(question)
        dic.update({"bridge_field_id": question.bridge_field_id.id})
        return dic

    @api.constrains("question_and_page_ids")
    def _check_question_and_page_ids(self):
        """
        1. Verifies that all bridge fields (if set) correspond to a field
        from membership.request
        2. Verifies that two questions never have the same bridge_field_id (if set).
        3. Verifies that for each question with a bridge field,
           the type of field on bridge field has to correspond with the type of answer
           for the question to the survey. Example: if self.question_type == 'date'
           then self.bridge_field_id.ttype has to be equal to Date.
        """
        for survey in self:
            questions_with_bridge_field = self.env["survey.question"].search(
                [("survey_id", "=", survey.id), ("bridge_field_id", "!=", False)]
            )
            #  1.
            models = questions_with_bridge_field.mapped("bridge_field_id.model")
            if not set(models).issubset({"membership.request"}):
                raise ValidationError(
                    _(
                        "At least one question has a bridge field "
                        "that is not a field from membership.request."
                    )
                )
            #  2.
            used_bridge_field_ids = []
            for question in questions_with_bridge_field:
                if question.bridge_field_id.id in used_bridge_field_ids:
                    raise ValidationError(
                        _(
                            "Several questions have the same bridge field "
                            "named %(bridge_field_name)s."
                        )
                        % {
                            "bridge_field_name": self.env["ir.model.fields"]
                            .browse(question.bridge_field_id.id)
                            .name
                        }
                    )
                used_bridge_field_ids.append(question.bridge_field_id.id)
            # 3.
            for question in questions_with_bridge_field:
                if question.question_type in self._get_dic().keys():
                    expected_type_of_answer = self._get_expected_type_of_answer(
                        question
                    )
                    if question.bridge_field_id.ttype not in expected_type_of_answer:
                        raise ValidationError(
                            _(
                                "The answer to question %(question)s will be of type "
                                "%(type_answer)s while the type of "
                                "the bridge field is %(type_bridge_field)s."
                            )
                            % {
                                "question": question.title,
                                "type_answer": expected_type_of_answer,
                                "type_bridge_field": question.bridge_field_id.ttype,
                            }
                        )
