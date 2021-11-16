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
        self.template = (self.env["event.type"]).create(
            {
                "name": "Test Template",
                "question_ids": [
                    (
                        0,
                        0,
                        {
                            "title": "Text input question",
                            "question_type": "text_box",
                            "interest_ids": [
                                (0, 0, {"name": "First interest"}),
                                (0, 0, {"name": "Second interest"}),
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
            self.template, an event template containing a question with interests
        Test case:
            When loading the event template, the interests on the question are
            well loaded too.
        """

        self.event.write({"event_type_id": self.template})
        self.assertEqual(
            len(self.event.question_ids[0].interest_ids),
            2,
            "Two interests should have been loaded.",
        )
