# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component
from odoo.addons.survey.controllers.main import Survey

from ..pydantic_models.survey_info import SurveyInfo, SurveyShortInfo
from ..pydantic_models.survey_search_filter import SurveySearchFilter
from ..pydantic_models.survey_user_info import SurveyUserInputInfo
from ..pydantic_models.survey_user_request import SurveyUserInputRequest


class SurveyService(Component):
    _inherit = "base.survey.rest.service"
    _name = "survey.rest.service"
    _usage = "survey"
    _expose_model = "survey.survey"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(SurveyInfo),
    )
    def get(self, _id: int) -> SurveyInfo:
        survey = self._get(_id)
        return SurveyInfo.from_orm(survey)

    def _get_search_domain(self, filters):
        domain = []
        if filters.title:
            domain.append(("title", "ilike", filters.title))
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.publish_date_before:
            domain.append(("publish_date", "<", filters.publish_date_before))
        if filters.publish_date_after:
            domain.append(("publish_date", ">", filters.publish_date_after))
        if filters.interest_ids:
            domain.append(("interest_ids", "in", filters.interest_ids))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(SurveySearchFilter),
        output_param=PydanticModelList(SurveyShortInfo),
    )
    def search(self, survey_search_filter: SurveySearchFilter) -> List[SurveyShortInfo]:
        domain = self._get_search_domain(survey_search_filter)
        res: List[SurveyShortInfo] = []
        for e in self.env[self._expose_model].sudo().search(domain):
            res.append(SurveyShortInfo.from_orm(e))
        return res

    def _get_answer_from_request(self, input_data, question):
        if str(question.id) in input_data.user_input_lines:
            return input_data.user_input_lines[str(question.id)]
        return ""

    def _validate_input_structure(self, input_data):
        lines = input_data.user_input_lines
        errors = []
        for key in lines:
            question = self.env["survey.question"].search([("id", "=", int(key))])
            if not question:
                errors.append(
                    ValueError(_("The key %s does not correspond to a question.") % key)
                )
            if (
                question.question_type
                in [
                    "text_box",
                    "char_box",
                    "numerical_box",
                    "date",
                    "datetime",
                ]
                and not isinstance(lines[key], str)
            ):
                errors.append(
                    ValueError(
                        _("Type of answer to question with id %d should be a string")
                        % question.id
                    )
                )
            elif question.question_type == "simple_choice" and not isinstance(
                lines[key], str
            ):
                errors.append(
                    ValueError(
                        _(
                            "Type of answer to question with id %d "
                            "should be a string containing an id."
                        )
                        % question.id
                    )
                )
            else:
                if question.question_type == "multiple_choice" and not isinstance(
                    lines[key], list
                ):
                    errors.append(
                        ValueError(
                            _(
                                "Type of answer to question with id %d "
                                "should be a list of strings containing an id."
                            )
                            % question.id
                        )
                    )
                elif question.question_type == "matrix" and not isinstance(
                    lines[key], dict
                ):
                    errors.append(
                        ValueError(
                            _(
                                "Type of answer to question with id %d should be a "
                                "dict containing line_ids as keys and list of ids as values."
                            )
                            % question.id
                        )
                    )
        return errors

    @restapi.method(
        routes=[(["/<int:_id>/user_answer"], "POST")],
        input_param=PydanticModel(SurveyUserInputRequest),
        output_param=PydanticModel(SurveyUserInputInfo),
    )
    def user_answer(
        self, _id: int, input_data: SurveyUserInputRequest
    ) -> SurveyUserInputInfo:

        survey = self._get(_id)

        # Validate the input structure
        errors = self._validate_input_structure(input_data)
        if errors:
            message = "\n".join([str(e) for e in errors])
            raise ValidationError(_("Wrong input format: ") + message)

        # First create the survey_user_input record
        survey_user_input = self.env["survey.user_input"].create(
            {"survey_id": survey.id}
        )

        # Take all questions
        questions = survey.question_ids

        errors = {}
        # Prepare answers / comment by question, validate and save answers
        for question in questions:
            inactive_questions = survey_user_input._get_inactive_conditional_questions()
            if question in inactive_questions:
                continue
            answer_str = self._get_answer_from_request(input_data, question)
            answer, comment = Survey()._extract_comment_from_answers(
                question, answer_str
            )
            errors.update(question.validate_question(answer, comment))
            if not errors.get(question.id):
                survey_user_input.save_lines(question, answer, comment)

        if errors:
            raise ValidationError(_("There were errors during the submission process"))

        survey_user_input.write({"state": "done"})

        return SurveyUserInputInfo.from_orm(survey_user_input)
