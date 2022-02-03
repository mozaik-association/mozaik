# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.component.core import WorkContext
from odoo.addons.extendable.tests.common import ExtendableMixin


class SurveyCase(BaseRestCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        collection = _PseudoCollection("survey.rest.services", cls.env)
        cls.services_env = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=request,
        )
        cls.service = cls.services_env.component(usage="survey")
        cls.survey = cls.env["survey.survey"].create(
            {
                "title": "Test Survey",
            }
        )
        cls.question_text_box = cls.env["survey.question"].create(
            {
                "survey_id": cls.survey.id,
                "title": "Explain who you are",
                "question_type": "text_box",
            }
        )
        cls.question_char_box = cls.env["survey.question"].create(
            {
                "survey_id": cls.survey.id,
                "title": "Enter your email",
                "question_type": "char_box",
            }
        )
        cls.question_numerical_box = cls.env["survey.question"].create(
            {
                "survey_id": cls.survey.id,
                "title": "What's your age?",
                "question_type": "numerical_box",
            }
        )
        cls.question_date = cls.env["survey.question"].create(
            {
                "survey_id": cls.survey.id,
                "title": "What's your birthdate",
                "question_type": "date",
            }
        )
        cls.question_datetime = cls.env["survey.question"].create(
            {
                "survey_id": cls.survey.id,
                "title": "When do you want to meet?",
                "question_type": "datetime",
            }
        )
        cls.question_simple_choice = cls.env["survey.question"].create(
            {
                "survey_id": cls.survey.id,
                "title": "Do you eat meat?",
                "question_type": "simple_choice",
                "suggested_answer_ids": [
                    (0, 0, {"value": "yes"}),
                    (0, 0, {"value": "no"}),
                ],
            }
        )
        cls.question_multiple_choice = cls.env["survey.question"].create(
            {
                "survey_id": cls.survey.id,
                "title": "What are your favourite fruits?",
                "question_type": "multiple_choice",
                "suggested_answer_ids": [
                    (0, 0, {"value": "apple"}),
                    (0, 0, {"value": "strawberry"}),
                    (0, 0, {"value": "raspberry"}),
                    (0, 0, {"value": "mango"}),
                ],
            },
        )
        cls.question_matrix = cls.env["survey.question"].create(
            {
                "survey_id": cls.survey.id,
                "title": "When is your favourite day for ...",
                "question_type": "matrix",
                "matrix_row_ids": [
                    (0, 0, {"value": "working"}),
                    (0, 0, {"value": "going on holidays"}),
                    (0, 0, {"value": "cooking"}),
                ],
                "suggested_answer_ids": [
                    (0, 0, {"value": "Monday"}),
                    (0, 0, {"value": "Tuesday"}),
                    (0, 0, {"value": "Friday"}),
                    (0, 0, {"value": "Saturday"}),
                ],
            },
        )

        cls.setUpExtendable()

    # pylint: disable=W8106
    def setUp(self):
        # resolve an inheritance issue (common.TransactionCase does not call
        # super)
        BaseRestCase.setUp(self)
        ExtendableMixin.setUp(self)

    def test_get_survey(self):
        self.service.dispatch("get", self.survey.id)

    def test_register_survey(self):
        vals = {
            "user_input_line_ids": {str(self.question_text_box.id): "Dummy answer"},
        }
        answer = self.service.dispatch("user_answer", self.survey.id, params=vals)
        self.env["survey.user_input"].browse(answer["id"])
