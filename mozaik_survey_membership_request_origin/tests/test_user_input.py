# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mozaik_survey_membership_request_involvement.tests import (
    test_user_input,
)


class TestSurveyUserInput(test_user_input.TestSurveyUserInput):
    def test_create_mr(self):
        answers = self.public_user_answers(self.answer_data)

        # We look for the associated membership request
        mr = self.env["membership.request"].search(
            [("survey_user_input_id", "=", answers.id)]
        )
        survey_origin = self.env.ref(
            "mozaik_survey_membership_request_origin.membership_request_origin_survey"
        )
        self.assertEqual(len(mr), 1)
        self.assertEqual(mr.origin_id.id, survey_origin.id)
