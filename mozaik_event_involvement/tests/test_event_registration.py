# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestEventRegistration(TransactionCase):
    def setUp(self):
        super().setUp()
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

    def test_membership_request_parameters(self):
        """
        An attendee was registered in setUp
        Verifies that:
            - the instance of the membership request is the instance of the event
            - the effective_time of the membership request is the begin date of the event
        """
        self.assertEqual(
            len(self.mr.int_instance_ids),
            1,
            "We should have a unique internal instance. ",
        )
        self.assertEqual(
            self.mr.int_instance_ids[0],
            self.event.int_instance_id,
            "The instance of the membership request should be the one of the event.",
        )
        self.assertEqual(
            self.mr.effective_time,
            self.event.date_begin,
            "The involvement date should be the same as the begin date of the event.",
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

    def test_auto_accept_membership(self):
        """
        Test case:
            When allowing auto acceptance of membership requests, and when
            the attendee registering is a partner of the DB,
            with a membership status equal to 'without_membership',
            partner field of the membership_request should be filled and
            auto acceptance of the membership request should work.
            We check that self.partner became a supporter.
        """
        self.event.write({"auto_accept_membership": True})
        self.register_attendee(
            lastname=self.partner.lastname,
            firstname=self.partner.firstname,
            email=self.partner.email,
            event=self.event,
        )
        self.assertEqual(
            self.partner.membership_state_id.code,
            "supporter",
            "Our partner should have become a supporter.",
        )

    def test_involvement_on_event(self):
        """
        The partner will subscribe to the event.
        We check that the partner has a new involvement:
        - the involvement_category is the one having the id of the event
        - the involvement_date is the begin date of the event
        - the interests on the event are present on the involvement
        """
        self.event.write(
            {
                "interest_ids": [
                    (0, 0, {"name": "First interest"}),
                    (0, 0, {"name": "Second interest"}),
                ]
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

        self.assertEqual(
            len(self.partner.partner_involvement_ids),
            1,
            "There should be one involvement",
        )
        involvement = self.partner.partner_involvement_ids[0]
        self.assertEqual(
            involvement.involvement_category_id.event_id.id,
            self.event.id,
            "The involvement category should correspond to the event.",
        )
        self.assertEqual(
            involvement.interest_ids,
            self.event.interest_ids,
            "The involvement should have the same interests as the event.",
        )
        self.assertEqual(
            involvement.effective_time,
            self.event.date_begin,
            "The involvement date should be the begin date of the event.",
        )

    def test_involvement_on_questions(self):
        """
        The partner will subscribe to the event and answer the questions.
        We check that the involvements corresponding to the questions were
        correctly created.
        """
        question_select = self.env["event.question"].create(
            {
                "title": "Do you eat meat?",
                "question_type": "simple_choice",
                "event_id": self.event.id,
                "answer_ids": [
                    (0, 0, {"name": "Yes"}),
                    (
                        0,
                        0,
                        {
                            "name": "No",
                            "interest_ids": [(0, 0, {"name": "vegetarian"})],
                        },
                    ),
                ],
            }
        )

        self.event.write({"question_ids": [(4, question_select.id)]})

        # Register the partner to the event
        answers = [
            (
                0,
                0,
                {
                    "question_id": question_select.id,
                    "value_answer_id": question_select.answer_ids.filtered(
                        lambda a: a.name == "No"
                    ).id,
                },
            )
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
        # Find the created membership request
        domain = [
            ("lastname", "=", self.attendee_partner.lastname),
            ("firstname", "=", self.attendee_partner.firstname),
            ("email", "=", self.attendee_partner.email),
        ]
        self.mr_partner = self.env["membership.request"].search(domain)
        # Validate this request
        self.mr_partner.validate_request()

        self.assertEqual(
            len(self.partner.partner_involvement_ids),
            2,
            "There should be two involvements",
        )

        involvement_question_select = self.partner.partner_involvement_ids.filtered(
            lambda pi: pi.question_event_id == question_select
        )

        self.assertEqual(
            involvement_question_select.interest_ids,
            question_select.answer_ids.filtered(lambda a: a.name == "No").interest_ids,
            "Since the attendee answered 'No', he should have the interest 'vegetarian'.",
        )
