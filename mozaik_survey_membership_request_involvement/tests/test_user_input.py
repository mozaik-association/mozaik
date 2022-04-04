# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from odoo.addons.survey.tests import test_survey_flow


class TestSurveyUserInput(test_survey_flow.TestSurveyFlow):
    def setUp(self):
        """
        We create a survey with 4 questions having a bridge field:
        lastname, firstname, birthdate, email.
        """
        super().setUp()

        self.ic = self.env["partner.involvement.category"].create(
            {
                "name": "Test involvement category",
                "interest_ids": [(0, 0, {"name": "Test interest"})],
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        self.survey = self.env["survey.survey"].create(
            {
                "title": "Test Survey",
                "access_mode": "public",
                "users_login_required": False,
                "questions_layout": "page_per_section",
                "state": "open",
                "auto_accept_membership": False,
                "access_token": "b137640d-14d4-4748-9ef6-344caaaaaae",
            }
        )
        self.page_0 = self.env["survey.question"].create(
            {
                "is_page": True,
                "sequence": 1,
                "title": "Page1: Your Data",
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
            bridge_field_id=self.env["ir.model.fields"]
            .search([("model", "=", "membership.request"), ("name", "=", "lastname")])
            .id,
        )
        self.question_firstname = self._add_question(
            self.page_0,
            "Please enter your firstname.",
            "char_box",
            comments_allowed=False,
            constr_mandatory=False,
            survey_id=self.survey.id,
            bridge_field_id=self.env["ir.model.fields"]
            .search([("model", "=", "membership.request"), ("name", "=", "firstname")])
            .id,
        )
        self.question_birthdate = self._add_question(
            self.page_0,
            "Please enter your birthdate.",
            "date",
            comments_allowed=False,
            constr_mandatory=False,
            survey_id=self.survey.id,
            bridge_field_id=self.env["ir.model.fields"]
            .search(
                [("model", "=", "membership.request"), ("name", "=", "birthdate_date")]
            )
            .id,
        )
        self.question_email = self._add_question(
            self.page_0,
            "Please enter your email.",
            "char_box",
            comments_allowed=False,
            constr_mandatory=False,
            survey_id=self.survey.id,
            bridge_field_id=self.env["ir.model.fields"]
            .search([("model", "=", "membership.request"), ("name", "=", "email")])
            .id,
        )
        # Default answer_data
        self.answer_data = {
            self.question_lastname.id: {"value": ["Dupont"]},
            self.question_firstname.id: {"value": ["Jean"]},
            self.question_birthdate.id: {"value": ["1985-07-09"]},
            self.question_email.id: {"value": ["jd@test.com"]},
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

    def test_create_mr(self):
        """
        A public user answers the survey, we check that a membership
        request was created and that the fields on the mr
        were completed if they were mentioned as bridge fields.
        """
        answers = self.public_user_answers(self.answer_data)

        # We look for the associated membership request
        mr = self.env["membership.request"].search(
            [("survey_user_input_id", "=", answers.id)]
        )
        self.assertEqual(len(mr), 1)
        self.assertEqual(mr.lastname, "Dupont")
        self.assertEqual(mr.firstname, "Jean")
        self.assertEqual(mr.birthdate_date, date(1985, 7, 9))
        self.assertEqual(mr.email, "jd@test.com")
        self.assertEqual(mr.state, "confirm")

    def test_set_partner_on_survey(self):
        """
        A public answers the survey, we validate the
        membership request and check that the newly created
        partner was set on the survey
        """
        answers = self.public_user_answers(self.answer_data)

        # We look for the associated membership request
        mr = self.env["membership.request"].search(
            [("survey_user_input_id", "=", answers.id)]
        )
        self.assertEqual(len(mr), 1)
        mr.validate_request()
        self.assertEqual(
            mr.partner_id,
            answers.partner_id,
            "The partner was not set correctly",
        )

    def test_involvement_on_survey(self):
        """
        We add an involvement category on the survey itself.
        A public user will answers the survey.
        We check that the newly created partner has a new involvement and that
        the involvement_category is the one on the survey.
        We also check that the interest on the involvement category
        is now an interest of the partner.
        """
        self.survey.write(
            {"involvement_category_id": self.ic.id, "auto_accept_membership": True}
        )

        answers = self.public_user_answers(self.answer_data)

        partner = answers.partner_id

        self.assertEqual(
            len(partner.partner_involvement_ids),
            1,
            "There should be one involvement",
        )
        involvement = partner.partner_involvement_ids[0]
        self.assertEqual(
            involvement.involvement_category_id.id,
            self.survey.involvement_category_id.id,
            "The involvement category should correspond to the one on the survey.",
        )
        self.assertEqual(
            partner.interest_ids,
            self.survey.involvement_category_id.interest_ids,
            "The interest of the involvement category should have been"
            "loaded in the res.partner data.",
        )

    def get_next_sequence_for_question(self, page):
        return (
            page.question_ids[-1].sequence + 1
            if page.question_ids
            else page.sequence + 1
        )

    def test_involvement_on_questions(self):
        """
        We add multiple choice questions with involvements on answers.
        The partner will answer the survey.
        We check that the involvements corresponding to the questions were
        correctly created, and that the interests were loaded.
        Question 1: answers 'No, never' so an involvement should be created
        Question 2: answers 'Thursday' and 'Friday', so one involvement should be created
        Question 3: a tickbox question that is ticked, so the involvement
        should be created.
        Question 4: a tickbox question that is not ticked, so the involvement
        should not be created.
        """
        self.survey.write({"auto_accept_membership": True})
        # We do not use _add_question method from survey since the code is not
        # allowing to add involvement categories on answers.
        question_1 = self.env["survey.question"].create(
            {
                "title": "Do you eat meat?",
                "sequence": self.get_next_sequence_for_question(self.page_0),
                "page_id": self.page_0.id,
                "survey_id": self.survey.id,
                "question_type": "simple_choice",
                "suggested_answer_ids": [
                    (0, 0, {"value": "Yes, a lot"}),
                    (0, 0, {"value": "Sometimes"}),
                    (
                        0,
                        0,
                        {
                            "value": "No, never",
                            "involvement_category_id": self.env[
                                "partner.involvement.category"
                            ]
                            .create(
                                {
                                    "name": "Does not eat meat.",
                                    "interest_ids": [(0, 0, {"name": "vegetarian"})],
                                    "res_users_ids": [
                                        (4, self.env.ref("base.user_admin").id)
                                    ],
                                }
                            )
                            .id,
                        },
                    ),
                ],
            }
        )
        question_2 = self.env["survey.question"].create(
            {
                "title": "What days are your favorite?",
                "sequence": self.get_next_sequence_for_question(self.page_0),
                "page_id": self.page_0.id,
                "survey_id": self.survey.id,
                "question_type": "multiple_choice",
                "suggested_answer_ids": [
                    (0, 0, {"value": "Monday"}),
                    (0, 0, {"value": "Tuesday"}),
                    (0, 0, {"value": "Wednesday"}),
                    (0, 0, {"value": "Thursday"}),
                    (
                        0,
                        0,
                        {
                            "value": "Friday",
                            "involvement_category_id": self.env[
                                "partner.involvement.category"
                            ]
                            .create(
                                {
                                    "name": "Loves fridays",
                                    "res_users_ids": [
                                        (4, self.env.ref("base.user_admin").id)
                                    ],
                                }
                            )
                            .id,
                        },
                    ),
                ],
            }
        )
        question_3 = self.env["survey.question"].create(
            {
                "title": "Tick if you like the planet.",
                "sequence": self.get_next_sequence_for_question(self.page_0),
                "page_id": self.page_0.id,
                "survey_id": self.survey.id,
                "question_type": "simple_choice",
                "constr_mandatory": False,
                "suggested_answer_ids": [
                    (
                        0,
                        0,
                        {
                            "value": "I love the planet",
                            "involvement_category_id": self.env[
                                "partner.involvement.category"
                            ]
                            .create(
                                {
                                    "name": "Loves the planet",
                                    "interest_ids": [
                                        (0, 0, {"name": "ecology"}),
                                        (0, 0, {"name": "planet"}),
                                    ],
                                    "res_users_ids": [
                                        (4, self.env.ref("base.user_admin").id)
                                    ],
                                }
                            )
                            .id,
                        },
                    ),
                ],
            }
        )
        question_4 = self.env["survey.question"].create(
            {
                "title": "Tick if you want to receive newsletters.",
                "sequence": self.get_next_sequence_for_question(self.page_0),
                "page_id": self.page_0.id,
                "survey_id": self.survey.id,
                "question_type": "simple_choice",
                "constr_mandatory": False,
                "suggested_answer_ids": [
                    (
                        0,
                        0,
                        {
                            "value": "I want to receive newsletters",
                            "involvement_category_id": self.env[
                                "partner.involvement.category"
                            ]
                            .create(
                                {
                                    "name": "Wants to receive newsletter",
                                    "res_users_ids": [
                                        (4, self.env.ref("base.user_admin").id)
                                    ],
                                }
                            )
                            .id,
                        },
                    ),
                ],
            }
        )
        self.page_0.write(
            {
                "question_ids": [
                    (4, question_1.id),
                    (4, question_2.id),
                    (4, question_3.id),
                    (4, question_4.id),
                ]
            }
        )
        self.answer_data.update(
            {
                question_1.id: {"value": [question_1.suggested_answer_ids.ids[2]]},
                question_2.id: {
                    "value": [
                        question_2.suggested_answer_ids.ids[3],
                        question_2.suggested_answer_ids.ids[4],
                    ]
                },
                question_3.id: {"value": [question_3.suggested_answer_ids.ids[0]]},
            }
        )

        answer = self.public_user_answers(self.answer_data)
        partner = answer.partner_id

        self.assertEqual(
            len(partner.partner_involvement_ids),
            3,
            "There should be three involvements",
        )
        # We check that the involvements are the good ones.
        set_of_involvements = {
            "Does not eat meat.",
            "Loves fridays",
            "Loves the planet",
        }
        self.assertEqual(
            set_of_involvements,
            set(partner.partner_involvement_ids.mapped("involvement_category_id.name")),
        )

        self.assertEqual(
            len(partner.interest_ids),
            3,
            "There should be three interests",
        )
        # We check that the interests are the good ones.
        set_of_interests = {"vegetarian", "ecology", "planet"}
        self.assertEqual(set_of_interests, set(partner.interest_ids.mapped("name")))

    def test_no_answer_for_lastname(self):
        """
        If we do not give our lastname, the encoded lastname
        should be UNKNOWN PERSON and we wouldn't be able
        to validate such a membership request.
        """
        # Remove answer containing lastname
        self.answer_data.pop(self.question_lastname.id)
        answers = self.public_user_answers(self.answer_data)

        # We look for the associated membership request
        mr = self.env["membership.request"].search(
            [("survey_user_input_id", "=", answers.id)]
        )
        self.assertEqual(len(mr), 1)

        # We try to validate it, it shouldn't work
        mr.validate_request()
        self.assertEqual(mr.state, "confirm")
