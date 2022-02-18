# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

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
        self.event = self.env["event.event"].create(
            {
                "name": "Test Event",
                "date_begin": datetime(2021, 11, 8, 12, 00, 00),
                "date_end": datetime(2021, 11, 13, 12, 00, 00),
                "auto_accept_membership": False,
            }
        )
        self.attendee = self.env["event.registration"].create(
            {
                "lastname": "Dupont",
                "firstname": "Jean",
                "email": "test@example.com",
                "event_id": self.event.id,
            }
        )

        domain = [
            ("lastname", "=", self.attendee.lastname),
            ("firstname", "=", self.attendee.firstname),
            ("email", "=", self.attendee.email),
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
        An attendee was registered in setUp.
        Verifies that the membership request was correctly created
        """
        self.assertEqual(
            len(self.mr), 1, "A unique membership request should have been found."
        )

    def test_partner_set_after_validation(self):
        """
        When validating a membership request, the
        (newly created of existing) partner is set
        on the corresponding event registration.
        """
        self.mr.validate_request()
        self.assertEqual(
            self.mr.partner_id,
            self.attendee.associated_partner_id,
            "The partner was not set correctly",
        )

    def register_attendee(self, lastname, firstname, email, event):
        """
        Creates an event registration.
        """
        return self.env["event.registration"].create(
            {
                "lastname": lastname,
                "firstname": firstname,
                "email": email,
                "event_id": event.id,
            }
        )

    def test_capitalization_firstname_lastname(self):
        """
        When creating an event registration, we preprocess the
        values entered, so firstname, lastname and email are formatted.
        """
        self.env["event.registration"].create(
            {
                "lastname": "DUJ'AR.DÏN",
                "firstname": "éric-andré olivier vincent",
                "email": "Eric@duj.FR",
                "event_id": self.event.id,
            }
        )
        domain = [
            ("email", "=", "eric@duj.fr"),
        ]
        mr = self.env["membership.request"].search(domain)
        self.assertEqual(mr.firstname, "Éric-André Olivier Vincent")
        self.assertEqual(mr.lastname, "Duj'Ar.Dïn")

    def test_involvement_on_event(self):
        """
        We add an involvement category on the event itself.
        The partner will subscribe to the event.
        We check that the partner has a new involvement:
        - the involvement_category is the one on the event
        - the involvement_date is the begin date of the event
        We also check that the interest on the involvement category
          is now an interest of the partner
        """
        self.event.write(
            {
                "involvement_category_id": self.ic.id,
            }
        )
        # Register the partner to the event
        self.attendee_partner = self.register_attendee(
            lastname=self.partner.lastname,
            firstname=self.partner.firstname,
            email=self.partner.email,
            event=self.event,
        )
        # Find the created membership request
        domain = [
            ("lastname", "=", self.attendee_partner.lastname),
            ("firstname", "=", self.attendee_partner.firstname),
            ("email", "=", self.attendee_partner.email),
        ]
        self.mr_partner = self.env["membership.request"].search(domain)
        # Validate this request
        self.mr_partner.validate_request()

        # Check that the request has been validated
        self.assertFalse(
            self.mr_partner.active,
            "The membership request should not" "be active anymore.",
        )

        self.assertEqual(
            len(self.partner.partner_involvement_ids),
            1,
            "There should be one involvement",
        )
        involvement = self.partner.partner_involvement_ids[0]
        self.assertEqual(
            involvement.involvement_category_id.id,
            self.event.involvement_category_id.id,
            "The involvement category should correspond to the one on the event.",
        )
        self.assertEqual(
            self.partner.interest_ids,
            self.event.involvement_category_id.interest_ids,
            "The interest of the involvement category should have been"
            "loaded in the res.partner data.",
        )

    def test_involvement_on_questions(self):
        """
        The partner will subscribe to the event and answer the questions.
        We check that the involvements corresponding to the questions were
        correctly created.
        Question 1: answers 'No, never' so an involvement should be created
        Question 2: answers 'No', so no involvement should be created
        """
        question_1 = self.env["event.question"].create(
            {
                "title": "Do you eat meat?",
                "question_type": "simple_choice",
                "event_id": self.event.id,
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
        question_2 = self.env["event.question"].create(
            {
                "title": "Do you want to receive the newsletter?",
                "question_type": "simple_choice",
                "event_id": self.event.id,
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

        self.event.write(
            {
                "question_ids": [
                    (4, question.id) for question in [question_1, question_2]
                ],
                "auto_accept_membership": True,
            }
        )

        # Register the partner to the event
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
        ]
        self.attendee_partner = self.env["event.registration"].create(
            {
                "lastname": self.partner.lastname,
                "firstname": self.partner.firstname,
                "email": self.partner.email,
                "event_id": self.event.id,
                "registration_answer_ids": answers,
            }
        )
        self.assertEqual(
            len(self.partner.partner_involvement_ids),
            1,
            "There should be one involvement",
        )
        self.assertEqual(
            self.partner.partner_involvement_ids.involvement_category_id.name,
            "Does not eat meat.",
            "The involvement is not the good one.",
        )
        self.assertEqual(
            self.partner.interest_ids.name,
            "vegetarian",
            "The interest wasn't well loaded.",
        )

    def test_register_attendee_with_associated_partner(self):
        """
        We register an attendee to the event but specifying the
        associated_partner_id.
        We check that the mr was correctly created and that
        partner_id and associated_partner_id fields are
        correct after validation.
        """
        reg = self.env["event.registration"].create(
            {
                "associated_partner_id": self.partner.id,
                "event_id": self.event.id,
            }
        )
        # Search for the associated mr.
        domain = [
            ("lastname", "=", self.partner.lastname),
            ("firstname", "=", self.partner.firstname),
        ]
        mr = self.env["membership.request"].search(domain)
        self.assertEqual(len(mr), 1)

        mr.validate_request()

        self.assertEqual(reg.associated_partner_id, self.partner)
