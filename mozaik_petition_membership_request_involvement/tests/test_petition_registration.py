# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase


class TestEventRegistration(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ic = self.env["partner.involvement.category"].create(
            {
                "name": "Test involvement category",
                "interest_ids": [(0, 0, {"name": "Test interest"})],
            }
        )
        self.petition = self.env["petition.petition"].create(
            {
                "title": "Test Petition",
                "date_begin": date(2021, 11, 8),
                "date_end": date(2021, 11, 13),
                "auto_accept_membership": False,
            }
        )

        self.signatory = self.env["petition.registration"].create(
            {
                "lastname": "Dupont",
                "firstname": "Jean",
                "email": "test@example.com",
                "petition_id": self.petition.id,
            }
        )
        domain = [
            ("lastname", "=", self.signatory.lastname),
            ("firstname", "=", self.signatory.firstname),
            ("email", "=", self.signatory.email),
        ]
        self.mr = self.env["membership.request"].search(domain)

        ms = self.env["membership.state"].search([("code", "=", "without_membership")])
        self.partner = self.env["res.partner"].create(
            {
                "lastname": "Rouve",
                "firstname": "Paul",
                "email": "rouve.paul@mail.com",
                "membership_state_id": ms.id,
            }
        )

    def test_membership_request_created(self):
        """
        An signatory was registered in setUp.
        Verifies that the membership request was correctly created
        """
        self.assertEqual(
            len(self.mr), 1, "A unique membership request should have been found."
        )

    def test_partner_set_after_validation(self):
        """
        When validating a membership request, the
        (newly created of existing) partner is set
        on the corresponding petition registration.
        """
        self.mr.validate_request()
        self.assertEqual(
            self.mr.partner_id,
            self.signatory.partner_id,
            "The partner was not set correctly",
        )

    def register_signatory(self, lastname, firstname, email, petition):
        """
        Creates a petition registration.
        """
        return self.env["petition.registration"].create(
            {
                "lastname": lastname,
                "firstname": firstname,
                "email": email,
                "petition_id": petition.id,
            }
        )

    def test_involvement_on_petition(self):
        """
        We add an involvement category on the petition itself.
        The partner will sign the petition.
        We check that the partner has a new involvement and that
        the involvement_category is the one on the petition.
        We also check that the interest on the involvement category
          is now an interest of the partner
        """
        self.petition.write(
            {
                "involvement_category_id": self.ic.id,
            }
        )
        # Register the partner to the petition
        self.signatory_partner = self.register_signatory(
            lastname=self.partner.lastname,
            firstname=self.partner.firstname,
            email=self.partner.email,
            petition=self.petition,
        )
        # Find the created membership request
        domain = [
            ("lastname", "=", self.signatory_partner.lastname),
            ("firstname", "=", self.signatory_partner.firstname),
            ("email", "=", self.signatory_partner.email),
        ]
        self.mr_partner = self.env["membership.request"].search(domain)
        # Validate this request
        self.mr_partner.validate_request()

        # Check that the request has been validated
        self.assertFalse(
            self.mr_partner.active,
            "The membership request should not be active anymore.",
        )

        self.assertEqual(
            len(self.partner.partner_involvement_ids),
            1,
            "There should be one involvement",
        )
        involvement = self.partner.partner_involvement_ids[0]
        self.assertEqual(
            involvement.involvement_category_id.id,
            self.petition.involvement_category_id.id,
            "The involvement category should correspond to the one on the petition.",
        )
        self.assertEqual(
            self.partner.interest_ids,
            self.petition.involvement_category_id.interest_ids,
            "The interest of the involvement category should have been"
            "loaded in the res.partner data.",
        )

    def test_involvement_on_questions(self):
        """
        The partner will sign the petition and answer the questions.
        We check that the involvements corresponding to the questions were
        correctly created.
        Question 1: answers 'No, never' so an involvement should be created
        Question 2: answers 'No', so no involvement should be created
        Question 3: a tickbox question that is ticked, so the involvement
        should be created.
        Question 4: a tickbox question that is not ticked, so the involvement
        should not be created.
        """
        question_1 = self.env["petition.question"].create(
            {
                "title": "Do you eat meat?",
                "question_type": "simple_choice",
                "petition_id": self.petition.id,
                "answer_ids": [
                    (0, 0, {"name": "Yes, a lot"}),
                    (0, 0, {"name": "Sometimes"}),
                    (
                        0,
                        0,
                        {
                            "name": "No, never",
                            "involvement_category_id": self.env[
                                "partner.involvement.category"
                            ]
                            .create(
                                {
                                    "name": "Does not eat meat.",
                                    "interest_ids": [(0, 0, {"name": "vegetarian"})],
                                },
                            )
                            .id,
                        },
                    ),
                ],
            }
        )
        question_2 = self.env["petition.question"].create(
            {
                "title": "Do you want to receive the newsletter?",
                "question_type": "simple_choice",
                "petition_id": self.petition.id,
                "answer_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Yes",
                            "involvement_category_id": self.env[
                                "partner.involvement.category"
                            ]
                            .create({"name": "Newsletter"})
                            .id,
                        },
                    ),
                    (0, 0, {"name": "No"}),
                ],
            }
        )
        question_3 = self.env["petition.question"].create(
            {
                "title": "Do you accept the terms and conditions?",
                "question_type": "tickbox",
                "is_mandatory": True,
                "petition_id": self.petition.id,
                "involvement_category_id": self.env["partner.involvement.category"]
                .create(
                    {
                        "name": "Terms and conditions",
                        "interest_ids": [(0, 0, {"name": "accept_terms"})],
                    }
                )
                .id,
            }
        )
        question_4 = self.env["petition.question"].create(
            {
                "title": "Do you want to become a member?",
                "question_type": "tickbox",
                "is_mandatory": False,
                "petition_id": self.petition.id,
                "involvement_category_id": self.env["partner.involvement.category"]
                .create({"name": "Wants to become a member"})
                .id,
            }
        )
        self.petition.write(
            {
                "question_ids": [
                    (4, question.id)
                    for question in [question_1, question_2, question_3, question_4]
                ],
                "auto_accept_membership": True,
            }
        )

        # Register the partner to the petition
        answers = [
            (
                0,
                0,
                {
                    "question_id": question_1.id,
                    "value_answer_id": question_1.answer_ids.filtered(
                        lambda a: a.name == "No, never"
                    ).id,
                },
            ),
            (
                0,
                0,
                {
                    "question_id": question_2.id,
                    "value_answer_id": question_2.answer_ids.filtered(
                        lambda a: a.name == "No"
                    ).id,
                },
            ),
            (
                0,
                0,
                {
                    "question_id": question_3.id,
                    "value_tickbox": True,
                },
            ),
        ]
        self.signatory_partner = self.env["petition.registration"].create(
            {
                "lastname": self.partner.lastname,
                "firstname": self.partner.firstname,
                "email": self.partner.email,
                "petition_id": self.petition.id,
                "registration_answer_ids": answers,
            }
        )
        self.assertEqual(
            len(self.partner.partner_involvement_ids),
            2,
            "There should be two involvements",
        )
        self.assertEqual(
            set(
                self.partner.partner_involvement_ids.mapped(
                    "involvement_category_id.name"
                )
            ),
            {"Does not eat meat.", "Terms and conditions"},
            "The involvements are not the good ones.",
        )
        self.assertEqual(
            set(self.partner.interest_ids.mapped("name")),
            {"vegetarian", "accept_terms"},
            "The interests weren't well loaded.",
        )
