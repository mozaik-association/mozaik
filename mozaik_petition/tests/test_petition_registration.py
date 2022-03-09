# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPetitionRegistration(TransactionCase):
    def setUp(self):
        super().setUp()

        self.mand_tick_1 = self.env["petition.question"].create(
            {
                "title": "Mandatory tickbox 1",
                "question_type": "tickbox",
                "is_mandatory": True,
            }
        )
        self.mand_tick_2 = self.env["petition.question"].create(
            {
                "title": "Mandatory tickbox 2",
                "question_type": "tickbox",
                "is_mandatory": True,
            }
        )
        self.not_mand_tick = self.env["petition.question"].create(
            {
                "title": "Not mandatory tickbox",
                "question_type": "tickbox",
                "is_mandatory": False,
            }
        )
        self.open_qu = self.env["petition.question"].create(
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

        self.milestone = self.env["petition.milestone"].create({"value": 1})
        self.petition = (self.env["petition.petition"]).create(
            {
                "title": "Test Petition",
                "date_begin": date(2021, 10, 13),
                "date_end": date(2021, 10, 16),
                "milestone_ids": [(6, 0, self.milestone.id)],
                "question_ids": question_ids,
            }
        )

    def test_petition_registration_without_answer_to_mandatory_questions(self):
        """
        self.petition contains 2 mandatory tickbox questions.
        We test that, for these questions
        1) When registering, if we answer to the question, the tickbox has to be ticked
        2) When registering, we have to answer to mandatory questions
        """

        values = {
            "firstname": "Jean",
            "lastname": "Dupont",
            "email": "jean.dupont@test.com",
            "petition_id": self.petition.id,
            "registration_answer_ids": False,
        }
        # Trying to register without answering to any question
        with self.assertRaises(ValidationError):
            self.env["petition.registration"].create(values)

        # Answering to a mandatory tickbox question without ticking it
        first_answer = {
            "question_id": self.mand_tick_1.id,
            "question_type": self.mand_tick_1.question_type,
            "is_mandatory": self.mand_tick_1.is_mandatory,
            "value_tickbox": False,
        }
        values.update({"registration_answer_ids": [(0, 0, first_answer)]})
        with self.assertRaises(ValidationError):
            self.env["petition.registration"].create(values)

        # Answering completely to this question, but not to the second
        # mandatory question
        first_answer.update({"value_tickbox": True})
        values.update({"registration_answer_ids": [(0, 0, first_answer)]})
        with self.assertRaises(ValidationError):
            self.env["petition.registration"].create(values)

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
            self.env["petition.registration"].create(values)

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
        attendee = self.env["petition.registration"].create(values)
        self.assertEqual(attendee.lastname, "Dupont")
        self.assertEqual(len(attendee.registration_answer_ids), 3)

    def test_unique_registration(self):
        """
        A given email address can sign a given petition only once.
        """
        self.env["petition.registration"].create(
            {
                "firstname": "Omar",
                "lastname": "Sy",
                "email": "o.s@test.com",
                "petition_id": self.petition.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["petition.registration"].create(
                {
                    "firstname": "Oscar",
                    "lastname": "Sauvage",
                    "email": "o.s@test.com",
                    "petition_id": self.petition.id,
                }
            )
        # A given person can register with a second address.
        self.env["petition.registration"].create(
            {
                "firstname": "Omar",
                "lastname": "Sy",
                "email": "omar.sy@test.com",
                "petition_id": self.petition.id,
            }
        )
