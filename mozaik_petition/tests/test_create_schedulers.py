# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from ..tests.common import TestPetitionCommon


class TestCreateSchedulers(TestPetitionCommon):
    def test_schedulers_creation(self):
        self.assertEqual(
            len(self.after_sub_scheduler), 1, "petition: wrong scheduler creation"
        )
        self.assertEqual(
            self.after_sub_scheduler.scheduled_date,
            self.test_petition.create_date.date(),
        )
        self.assertTrue(self.after_sub_scheduler.done)

        self.assertEqual(
            len(self.after_sub_scheduler_2), 1, "petition: wrong scheduler creation"
        )
        self.assertEqual(
            self.after_sub_scheduler_2.scheduled_date,
            self.test_petition.create_date.date() + relativedelta(days=1),
        )
        self.assertTrue(self.after_sub_scheduler_2.done)

        self.assertEqual(
            len(self.petition_prev_scheduler), 1, "petition: wrong scheduler creation"
        )
        self.assertEqual(
            self.petition_prev_scheduler.scheduled_date,
            self.petition_date_begin + relativedelta(days=-1),
        )
        self.assertFalse(self.petition_prev_scheduler.done)

        self.assertEqual(
            len(self.petition_next_scheduler), 1, "petition: wrong scheduler creation"
        )
        self.assertEqual(
            self.petition_next_scheduler.scheduled_date,
            self.petition_date_end + relativedelta(days=1),
        )
        self.assertFalse(self.petition_next_scheduler.done)
