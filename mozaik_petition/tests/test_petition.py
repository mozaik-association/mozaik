# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestPetition(TransactionCase):
    def setUp(self):
        super().setUp()
        self.petition = (self.env["petition.petition"]).create(
            {
                "title": "title",
                "date_begin": date(2021, 10, 13),
                "date_end": date(2021, 10, 16),
            }
        )
        self.template1 = (self.env["petition.type"]).create(
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

    def test_check_date(self):
        """
        Data:
            /
        Test case:
            When creating a petition with an end date
            before the beginning date, an error has to be raised.
        """
        with self.assertRaises(ValidationError):
            self.env["petition.petition"].create(
                {
                    "title": "TestPetition",
                    "date_begin": fields.Date.today() + relativedelta(days=1),
                    "date_end": fields.Date.today() + relativedelta(days=-1),
                }
            )

    def test_changing_question_type_if_answers(self):
        """
        Data (defined in the function):
            self.question, a question
            self.signatory, a signatory adding an answer to the question self.question
        Test case:
            It should be impossible to change the type of a question
            if it already has answers
        """
        self.question = (self.env["petition.question"]).create(
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
        self.signatory = (self.env["petition.registration"]).create(
            {
                "petition_id": self.petition.id,
                "email": "test@test.com",
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
             self.petition : a test petition
             self.template1 : a template containing 3 questions
        Data (defined in this function):
            self.template2 : a template containing 1 question
            self.signatory : a signatory answering to the question of self.petition
        Test case:
            - When self.petition.petition_type_id is template1,
            there are 3 associated questions.
            - When self.petition.petition_type_id turns to template2,
            there is only 1 associated question.
        """

        self.template2 = (self.env["petition.type"]).create(
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

        # When assigning template 1 to self.petition,
        # 3 questions are automatically encoded.
        self.petition.write({"petition_type_id": self.template1})
        self.assertEqual(
            len(self.petition.question_ids), 3, "There should be 3 questions."
        )

        # Changing to template 2: all questions from template 1 are erased.
        self.petition.write({"petition_type_id": self.template2})
        self.assertEqual(
            len(self.petition.question_ids), 1, "There should only be 1 question."
        )
        self.assertEqual(
            self.petition.question_ids[0].title,
            "Mandatory tickbox",
            "The remaining question should be the one of template 2",
        )
