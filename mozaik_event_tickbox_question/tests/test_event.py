from datetime import date

from odoo.exceptions import UserError
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

    def test_changing_question_type_if_answers(self):
        """
        Data (defined in setUp):
            self.event, a test event
        Data (defined in the function):
            self.question, a question
            self.signatory, a signatory adding an answer to the question self.question
        Test case:
            It should be impossible to change the type of a question
            if it already has answers
        """
        self.question = (self.env["event.question"]).create(
            {
                "title": "Test question",
                "question_type": "simple_choice",
            }
        )
        self.assertEqual(
            self.question.question_type,
            "simple_choice",
            "Question type should be simple_choice",
        )

        # Changing question type without any answer
        self.question.write({"question_type": "text_box"})
        self.assertEqual(
            self.question.question_type, "text_box", "Question type should be text_box"
        )

        # Adding an answer
        self.attendee = (self.env["event.registration"]).create(
            {
                "event_id": self.event.id,
                "registration_answer_ids": [
                    (
                        0,
                        0,
                        {
                            "question_id": self.question.id,
                            "value_text_box": "Answer",
                        },
                    )
                ],
            }
        )

        # Changing question type with an answer -> should not be permitted
        with self.assertRaises(UserError):
            self.question.write({"question_type": "tickbox"})

    def test_changing_question_type(self):
        """
        Data (defined in setUp):
            self.event : a test event
        Data (defined in this function):
            self.template1 : a template containing 3 questions
            self.template2 : a template containing 1 question
            self.attendee : an attendee answering to the question of self.event
        Test case:
            - When self.event.event_type_id is template1,
            there are 3 associated questions.
            - When self.event.event_type_id turns to template2,
            there is only 1 associated question.
        """

        self.template1 = (self.env["event.type"]).create(
            {
                "name": "Template 1",
                "question_ids": [
                    (0, 0, {"title": "Text input", "question_type": "text_box"}),
                    (
                        0,
                        0,
                        {
                            "title": "Tickbox",
                            "question_type": "tickbox",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "title": "Selection",
                            "answer_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "name": "Yes",
                                    },
                                ),
                                (
                                    0,
                                    0,
                                    {
                                        "name": "No",
                                    },
                                ),
                            ],
                        },
                    ),
                ],
            }
        )

        self.template2 = (self.env["event.type"]).create(
            {
                "name": "Template 2",
                "question_ids": [
                    (
                        0,
                        0,
                        {
                            "title": "Mandatory tickbox",
                            "is_mandatory": True,
                        },
                    )
                ],
            }
        )

        # When assigning template 1 to self.event,
        # 3 questions are automatically encoded.
        self.event.write({"event_type_id": self.template1})
        self.assertEqual(
            len(self.event.question_ids), 3, "There should be 3 questions."
        )

        # Changing to template 2: all questions from template 1 are erased.
        self.event.write({"event_type_id": self.template2})
        self.assertEqual(
            len(self.event.question_ids), 1, "There should only be 1 question."
        )
        self.assertEqual(
            self.event.question_ids[0].title,
            "Mandatory tickbox",
            "The remaining question should be the one of template 2",
        )

    def test_tickbox_question(self):
        """
        Data (defined in setUp):
            self.event : a test event
        Data (defined in the function):
            self.template, an event template containing a mandatory tickbox question
            with an interest on it.
        Test case:
            When loading the event template, the question is well set
            as mandatory and the interest is loaded.
        """
        self.template = (self.env["event.type"]).create(
            {
                "name": "Test Template",
                "question_ids": [
                    (
                        0,
                        0,
                        {
                            "title": "Mandatory tickbox question",
                            "question_type": "tickbox",
                            "is_mandatory": True,
                            "interest_ids": [(0, 0, {"name": "Interest"})],
                        },
                    )
                ],
            }
        )
        self.event.write({"event_type_id": self.template})
        self.assertEqual(
            self.event.question_ids[0].is_mandatory,
            True,
            "Field is_mandatory should be set to True",
        )
        self.assertEqual(
            self.event.question_ids[0].interest_ids[0].name,
            "Interest",
            "The interest was not loaded.",
        )
