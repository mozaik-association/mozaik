# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSurvey(TransactionCase):
    def setUp(self):
        super().setUp()

        self.suggested_answer_ids = [
            (0, 0, {"value": "Answer 1"}),
            (0, 0, {"value": "Answer 2"}),
        ]
        self.matrix_row_ids = [
            (0, 0, {"value": "Row 1"}),
            (0, 0, {"value": "Row 2"}),
        ]

    def test_loading_question_1_by_default(self):
        """
        When creating a new survey, question1 should be loaded by default
        with all its parameters.
        """
        question_1 = self.env["survey.question.by.default"].create(
            {
                "title": "Question 1",
                "question_type": "simple_choice",
                "suggested_answer_ids": self.suggested_answer_ids,
                "constr_mandatory": True,
            }
        )
        survey = self.env["survey.survey"].create(
            {
                "title": "Test survey",
            }
        )
        self.assertEqual(
            len(survey.question_and_page_ids), 1, "The question was not loaded."
        )
        question_on_survey = survey.question_and_page_ids[0]
        self.assertTrue(question_on_survey.constr_mandatory)
        self.assertEqual(question_on_survey.question_type, question_1.question_type)
        self.assertEqual(
            set(question_on_survey.suggested_answer_ids.mapped("value")),
            set(question_1.suggested_answer_ids.mapped("value")),
            "The answers are not the same on the question by default and the question.",
        )

    def test_loading_question_2_by_default(self):
        """
        When creating a new survey, question2 should be loaded by default
        with all its parameters.
        """
        question_2 = self.env["survey.question.by.default"].create(
            {
                "title": "Question 2",
                "question_type": "matrix",
                "suggested_answer_ids": self.suggested_answer_ids,
                "matrix_row_ids": self.matrix_row_ids,
            }
        )
        survey = self.env["survey.survey"].create(
            {
                "title": "Test survey",
            }
        )
        self.assertEqual(
            len(survey.question_and_page_ids), 1, "The question was not loaded."
        )
        question_on_survey = survey.question_and_page_ids[0]
        self.assertEqual(question_on_survey.question_type, question_2.question_type)
        self.assertEqual(
            set(question_on_survey.suggested_answer_ids.mapped("value")),
            set(question_2.suggested_answer_ids.mapped("value")),
            "The answers are not the same on the question by default and the question.",
        )
        self.assertEqual(
            set(question_on_survey.matrix_row_ids.mapped("value")),
            set(question_2.matrix_row_ids.mapped("value")),
            "The rows are not the same on the question by default and the question.",
        )
