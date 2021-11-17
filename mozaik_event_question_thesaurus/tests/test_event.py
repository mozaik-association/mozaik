from datetime import date

from odoo.tests.common import TransactionCase


class TestEvent(TransactionCase):
    def setUp(self):
        super().setUp()
        self.event = (self.env["event.event"]).create(
            {
                "name": "Test Event",
                "date_begin": date(2021, 10, 13),
                "date_end": date(2021, 10, 16),
            }
        )
        interest_ids = [
            (0, 0, {"name": "First interest"}),
            (0, 0, {"name": "Second interest"}),
        ]
        more_interest_ids = [
            (0, 0, {"name": "Third interest"}),
        ]
        self.template = (self.env["event.type"]).create(
            {
                "name": "Test Template",
                "question_ids": [
                    (
                        0,
                        0,
                        {
                            "title": "Text input question",
                            "question_type": "simple_choice",
                            "answer_ids": [
                                (0, 0, {"name": "Yes", "interest_ids": interest_ids}),
                                (
                                    0,
                                    0,
                                    {"name": "No", "interest_ids": more_interest_ids},
                                ),
                            ],
                        },
                    )
                ],
            }
        )

    def test_interest_on_question(self):
        """
        Data:
            self.event : a test event
            self.template, an event template containing a selection question w
                ith interests on answers
        Test case:
            When loading the event template, the interests on the answers are
            well loaded too.
        """

        self.event.write({"event_type_id": self.template})
        interests_on_yes = (
            self.event.question_ids[0]
            .answer_ids.search([("name", "=", "Yes")])
            .interest_ids
        )
        interests_on_no = (
            self.event.question_ids[0]
            .answer_ids.search([("name", "=", "No")])
            .interest_ids
        )
        self.assertEqual(
            len(interests_on_yes),
            2,
            "Two interests should have been loaded for answer 'Yes'.",
        )
        self.assertEqual(
            len(interests_on_no),
            1,
            "One interest should have been loaded for answer 'No'.",
        )
