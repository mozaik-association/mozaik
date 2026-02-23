# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mozaik_survey_membership_request_involvement.tests.test_user_input import (  # noqa: B950 pylint: disable=line-too-long
    TestSurveyUserInput as BaseTestSurveyUserInput,
)


class TestSurveyUserInput(BaseTestSurveyUserInput):
    def test_answer_no_autovalidation(self):
        """
        Membership request is still in confirm.
        """
        self.survey.auto_accept_membership = False
        answers = self.public_user_answers(self.answer_data)

        mr = self.env["membership.request"].search(
            [("survey_user_input_id", "=", answers.id)]
        )
        self.assertEqual(len(mr), 1)
        self.assertEqual(mr.state, "confirm")

    def test_answer_complete_autovalidation(self):
        """
        Complete autovalidation case
        """
        self.survey.write(
            {
                "auto_accept_membership": True,
                "autovalidation_type": "complete",
            }
        )
        answers = self.public_user_answers(self.answer_data)

        mr = (
            self.env["membership.request"]
            .with_context(active_test=False)
            .search([("survey_user_input_id", "=", answers.id)])
        )
        self.assertEqual(len(mr), 1)
        self.assertEqual(mr.state, "validate")

    def test_answer_light_autovalidation(self):
        self.survey.write(
            {
                "auto_accept_membership": True,
                "autovalidation_type": "light",
            }
        )
        answers = self.public_user_answers(self.answer_data)

        mr = (
            self.env["membership.request"]
            .with_context(active_test=False)
            .search([("survey_user_input_id", "=", answers.id)])
        )
        self.assertEqual(len(mr), 1)
        self.assertEqual(mr.state, "light_autoval")
        self.assertTrue(mr.light_mr_id)
        self.assertEqual(mr.light_mr_id.state, "validate")
