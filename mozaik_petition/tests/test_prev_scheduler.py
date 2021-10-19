# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from ..tests.common import TestPetitionCommon


class TestPrevScheduler(TestPetitionCommon):
    def setUp(self):
        super().setUp()
        self._create_registrations()

    def test_prev_scheduler_before_scheduled_date(self):
        """
        Data:
            2 registrations
            A scheduler set one day before the beginning of the petition
            Time is set before the scheduled date
        Expected case:
            Nothing is sent
        """
        self.assertFalse(self.petition_prev_scheduler.mail_sent)
        self.assertFalse(self.petition_prev_scheduler.done)

        today_start = self.petition_date_begin + relativedelta(days=-2)
        with freeze_time(today_start), self.mock_mail_gateway():
            self.petition_prev_scheduler.execute()

        self.assertFalse(self.petition_prev_scheduler.mail_sent)
        self.assertFalse(self.petition_prev_scheduler.done)
        self.assertEqual(len(self._new_mails), 0)

    def test_executing_cron(self):
        """
        Data:
            2 registrations
            A scheduler set one day before the beginning of the petition
        Expected case:
            Running the cron, a mail to each attendee is sent
        """
        # execute cron to run schedulers
        today_start = self.petition_date_begin
        with freeze_time(today_start), self.mock_mail_gateway():
            self.petition_cron_id.method_direct_trigger()

        # check that scheduler is finished
        self.assertTrue(
            self.petition_prev_scheduler.mail_sent,
            "petition: reminder scheduler should have run",
        )
        self.assertTrue(
            self.petition_prev_scheduler.done,
            "petition: reminder scheduler should have run",
        )

        # check emails effectively sent
        self.assertEqual(
            len(self._new_mails),
            2,
            "petition: should have scheduled 2 mails (1 / registration)",
        )

    def test_after_new_registration(self):
        """
        Data:
            2 registrations for which we have already sent emails
        Expected case:
            When creating a new registration, the mail is not sent a second time
        """
        today_start = self.petition_date_begin + relativedelta(days=-1)
        with freeze_time(today_start), self.mock_mail_gateway():
            self.petition_cron_id.method_direct_trigger()
        self._create_third_registration()
        self.assertTrue(self.petition_prev_scheduler.mail_sent)
        self.assertTrue(self.petition_prev_scheduler.mail_sent)
