from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestEventRegistration(TransactionCase):
    def setUp(self):
        super().setUp()

        self.mand_tick_1 = self.env["event.question"].create(
            {
                "title": "Mandatory tickbox 1",
                "question_type": "tickbox",
                "is_mandatory": True,
            }
        )
        self.mand_tick_2 = self.env["event.question"].create(
            {
                "title": "Mandatory tickbox 2",
                "question_type": "tickbox",
                "is_mandatory": True,
            }
        )
        self.not_mand_tick = self.env["event.question"].create(
            {
                "title": "Not mandatory tickbox",
                "question_type": "tickbox",
                "is_mandatory": False,
            }
        )
        self.open_qu = self.env["event.question"].create(
            {
                "title": "Open question",
                "question_type": "text_box",
            }
        )

        question_ids = [
            (4, self.mand_tick_1.id),
            (4, self.mand_tick_2.id),
            (4, self.not_mand_tick.id),
            (4, self.open_qu.id),
        ]

        self.event = (self.env["event.event"]).create(
            {
                "name": "Test Event",
                "date_begin": date(2021, 10, 13),
                "date_end": date(2021, 10, 16),
                "question_ids": question_ids,
            }
        )

    def test_event_registration_without_answer_to_mandatory_questions(self):
        """
        self.event contains 2 mandatory tickbox questions.
        We test that, for these questions
        1) When registering, if we answer to the question, the tickbox has to be ticked
        2) When registering, we have to answer to mandatory questions
        """

        values = {
            "firstname": "Jean",
            "lastname": "Dupont",
            "event_id": self.event.id,
            "registration_answer_ids": False,
        }
        # Trying to register without answering to any question
        with self.assertRaises(ValidationError):
            self.env["event.registration"].create(values)

        # Answering to a mandatory tickbox question without ticking it
        first_answer = {
            "question_id": self.mand_tick_1.id,
            "question_type": self.mand_tick_1.question_type,
            "is_mandatory": self.mand_tick_1.is_mandatory,
            "value_tickbox": False,
        }
        values.update({"registration_answer_ids": [(0, 0, first_answer)]})
        with self.assertRaises(ValidationError):
            self.env["event.registration"].create(values)

        # Answering completely to this question, but not to the second
        # mandatory question
        first_answer.update({"value_tickbox": True})
        values.update({"registration_answer_ids": [(0, 0, first_answer)]})
        with self.assertRaises(ValidationError):
            self.env["event.registration"].create(values)

        # Answering to a second non mandatory question
        second_answer = {
            "question_id": self.open_qu.id,
            "question_type": self.open_qu.question_type,
            "value_text_box": "I answered!",
        }
        values.update(
            {"registration_answer_ids": [(0, 0, first_answer), (0, 0, second_answer)]}
        )
        with self.assertRaises(ValidationError):
            self.env["event.registration"].create(values)

        # Finally answering to the second mandatory question
        third_answer = {
            "question_id": self.mand_tick_2.id,
            "question_type": self.mand_tick_2.question_type,
            "is_mandatory": True,
            "value_tickbox": True,
        }
        values.update(
            {
                "registration_answer_ids": [
                    (0, 0, first_answer),
                    (0, 0, second_answer),
                    (0, 0, third_answer),
                ]
            }
        )
        attendee = self.env["event.registration"].create(values)
        self.assertEqual(attendee.lastname, "Dupont")
        self.assertEqual(len(attendee.registration_answer_ids), 3)

    def test_event_registration_involvement(self):
        """
        Register to an event, answering a tickbox question with an involvement category
        but not ticking it.
        -> Check that the involvement was not added on the membership request.

        Tick the checkbox
        -> Check that involvement was added on the membership request.
        """
        # Remove mandatory constraint as it is useless for this test
        self.mand_tick_1.is_mandatory = False
        self.mand_tick_2.is_mandatory = False
        # Add an involvement
        involvement_category = self.env["partner.involvement.category"].create(
            {"name": "IC"}
        )
        self.not_mand_tick.involvement_category_id = involvement_category
        # Register to the event
        attendee = self.env["event.registration"].create(
            {
                "firstname": "Jean",
                "lastname": "Dupont",
                "event_id": self.event.id,
                "registration_answer_ids": [
                    (
                        0,
                        0,
                        {
                            "question_id": self.not_mand_tick.id,
                            "question_type": self.not_mand_tick.question_type,
                            "value_tickbox": False,
                        },
                    )
                ],
            }
        )
        self.assertTrue(attendee.membership_request_id)
        self.assertFalse(attendee.membership_request_id.involvement_category_ids)

        # Register again, ticking the question
        attendee = self.env["event.registration"].create(
            {
                "firstname": "Jean",
                "lastname": "Dupont",
                "event_id": self.event.id,
                "registration_answer_ids": [
                    (
                        0,
                        0,
                        {
                            "question_id": self.not_mand_tick.id,
                            "question_type": self.not_mand_tick.question_type,
                            "value_tickbox": True,
                        },
                    )
                ],
            }
        )
        self.assertTrue(attendee.membership_request_id)
        self.assertEqual(
            attendee.membership_request_id.involvement_category_ids.ids,
            [involvement_category.id],
        )
