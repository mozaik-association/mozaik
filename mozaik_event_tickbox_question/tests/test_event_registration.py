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
        ms = self.env["membership.state"].search([("code", "=", "without_membership")])
        self.partner = self.env["res.partner"].create(
            {
                "lastname": "Rouve",
                "firstname": "Paul",
                "email": "rouve.paul@mail.com",
                "membership_state_id": ms.id,
            }
        )

    def test_involvement_on_questions(self):
        """
        We check that if there is a tickbox question in the event,
        the corresponding involvement is created and the interests
        are well loaded.
        """
        question_tickbox = self.env["event.question"].create(
            {
                "title": "Please tick this question",
                "question_type": "tickbox",
                "event_id": self.event.id,
                "is_mandatory": "True",
                "interest_ids": [(0, 0, {"name": "RGPD"})],
            }
        )

        self.event.write({"question_ids": [(4, question_tickbox.id)]})

        answers = [
            (
                0,
                0,
                {
                    "question_id": question_tickbox.id,
                    "value_tickbox": True,
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
        involvement_question_tickbox = self.partner.partner_involvement_ids.filtered(
            lambda pi: pi.question_event_id == question_tickbox
        )

        self.assertEqual(
            involvement_question_tickbox.interest_ids,
            question_tickbox.interest_ids,
            "The involvement concerning RGPD should have interest RGPD.",
        )
