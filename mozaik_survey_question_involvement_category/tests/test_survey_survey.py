# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSurvey(TransactionCase):
    def setUp(self):
        super().setUp()

        self.ic1 = self.env["partner.involvement.category"].create(
            {"name": "Involvement category 1"}
        )
        self.ic2 = self.env["partner.involvement.category"].create(
            {"name": "Involvement category 2"}
        )

        self.suggested_answer_ids = [
            (0, 0, {"value": "Answer 1", "involvement_category_id": self.ic1.id}),
            (0, 0, {"value": "Answer 2", "involvement_category_id": self.ic2.id}),
            (0, 0, {"value": "Answer 3"}),
        ]

    def test_loading_question_1_by_default(self):
        """
        When creating a new survey, the involvement categories
        present on the answers of question1 should be loaded.
        """
        question_1 = self.env["survey.question.by.default"].create(
            {
                "title": "Question 1",
                "question_type": "simple_choice",
                "suggested_answer_ids": self.suggested_answer_ids,
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
        self.assertEqual(question_on_survey.question_type, question_1.question_type)
        for answer in question_on_survey.suggested_answer_ids:
            self.assertEqual(
                len(
                    question_1.suggested_answer_ids.search(
                        [("value", "=", answer.value)]
                    )
                ),
                1,
            )
            self.assertEqual(
                question_1.suggested_answer_ids.search(
                    [("value", "=", answer.value)]
                ).involvement_category_id,
                answer.involvement_category_id,
            )
