# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.survey.tests import test_survey_flow


class TestSurveyUserInput(test_survey_flow.TestSurveyFlow):
    def setUp(self):
        """
        We create a survey with questions having scoring:
        - a numerical question
        - a simple choice question (with one correct answer)
        - a multiple choice question

        There are also questions without scoring.
        """
        super().setUp()

        self.survey = self.env["survey.survey"].create(
            {
                "title": "Test Survey",
                "access_mode": "public",
                "users_login_required": False,
                "questions_layout": "page_per_section",
                "state": "open",
                "access_token": "b137640d-14d4-4748-9ef6-344caaaaaae",
                "scoring_type": "scoring_without_answers",
                "exclude_not_answered_from_total": True,
            }
        )
        self.page_0 = self.env["survey.question"].create(
            {
                "is_page": True,
                "sequence": 1,
                "title": "Page1",
                "survey_id": self.survey.id,
            }
        )
        self.question_lastname = self._add_question(
            self.page_0,
            "Please enter your lastname.",
            "char_box",
            comments_allowed=False,
            constr_mandatory=False,
            survey_id=self.survey.id,
        )
        self.question_numerical = self._add_question(
            self.page_0,
            "What's the answer to 3+2?",
            "numerical_box",
            comments_allowed=False,
            constr_mandatory=False,
            survey_id=self.survey.id,
            answer_numerical_box=5,
            answer_score=10,
        )
        self.question_simple_choice = self._add_question(
            self.page_0,
            "How much is 4+5?",
            "simple_choice",
            comments_allowed=False,
            constr_mandatory=False,
            survey_id=self.survey.id,
            labels=[
                {"value": "1"},
                {"value": "5"},
                {"value": "9", "answer_score": "10", "is_correct": True},
            ],
        )
        self.question_multiple_choice = self._add_question(
            self.page_0,
            "Which days start with a 't'?",
            "multiple_choice",
            comments_allowed=False,
            constr_mandatory=False,
            survey_id=self.survey.id,
            labels=[
                {"value": "monday"},
                {"value": "tuesday", "answer_score": "5", "is_correct": True},
                {"value": "wednesday"},
                {"value": "thursday", "answer_score": "5", "is_correct": True},
                {"value": "friday"},
            ],
        )

        # Default answer_data
        self.answer_data = {
            self.question_lastname.id: {"value": ["Dupont"]},
            self.question_numerical.id: {"value": ["5"]},
            self.question_simple_choice.id: {
                "value": [self.question_simple_choice.suggested_answer_ids.ids[2]]
            },
            self.question_multiple_choice.id: {
                "value": [
                    self.question_multiple_choice.suggested_answer_ids.ids[i]
                    for i in [1, 3]
                ]
            },
        }

    def public_user_answers(self, answer_data):
        """
        A public user accesses the survey and answers it.
        """
        # Customer opens start page
        self._access_start(self.survey)

        # An answer was created, we search for it
        answers = self.env["survey.user_input"].search(
            [("survey_id", "=", self.survey.id)]
        )
        answers.ensure_one()
        answer_token = answers.access_token

        # Customer access questions page
        r = self._access_page(self.survey, answer_token)
        csrf_token = self._find_csrf_token(r.text)
        self._access_begin(self.survey, answer_token)

        # Customer answers and submits
        post_data = self._format_submission_data(
            self.page_0,
            answer_data,
            {"csrf_token": csrf_token, "token": answer_token, "button_submit": "next"},
        )
        self._access_submit(self.survey, answer_token, post_data)
        answers.invalidate_cache()

        return answers

    def test_answering_all_questions_corectly(self):
        """
        If we answer all questions correctly, scoring should be the same
        as before: 100%.
        """
        answers = self.public_user_answers(self.answer_data)
        self.assertEqual(answers.scoring_percentage, 100)

    def test_removing_one_answer(self):
        """
        Removing the answer to numerical question -> if the other answers
        are correct, we keep a scoring percentage equal to 100%
        """
        self.answer_data.pop(self.question_numerical.id)
        answers = self.public_user_answers(self.answer_data)
        self.assertEqual(answers.scoring_percentage, 100)

    def test_removing_all_answers(self):
        """
        If the partner doesn't answer any question with a score, he gets 100%
        since they are not mandatory
        """
        answer_data = {self.question_lastname.id: {"value": ["Dupont"]}}
        answers = self.public_user_answers(answer_data)
        self.assertEqual(answers.scoring_percentage, 100)

    def test_one_not_answered_one_correct_one_false(self):
        """
        The partner skips 1 answer, and has 1 correct over 2 -> he gets 50%
        """
        self.answer_data.pop(self.question_simple_choice.id)
        self.answer_data[self.question_numerical.id] = {"value": ["20"]}
        answers = self.public_user_answers(self.answer_data)
        self.assertEqual(answers.scoring_percentage, 50)
