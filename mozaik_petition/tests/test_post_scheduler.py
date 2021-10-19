# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from ..tests.common import TestPetitionCommon


class TestPostScheduler(TestPetitionCommon):
    def setUp(self):
        super().setUp()
        self._create_registrations()

    def test_schedulers_untouched_after_registration(self):
        """
        Data:
            3 registrations at different dates, before the end of the petition
            A scheduler scheduled for 1 day after the end of the petition
            Actual time: during the petition
        Expected case:
            Nothing is sent.
        """
        self._create_third_registration()
        today_start = self.petition_date_begin
        with freeze_time(today_start), self.mock_mail_gateway():
            self.petition_cron_id.method_direct_trigger()
        self.assertFalse(self.petition_next_scheduler.mail_sent)
        self.assertFalse(self.petition_next_scheduler.done)

    def test_post_petition_scheduler(self):
        """
        Data:
            3 registrations at different dates, before the end of the petition
            A scheduler scheduled for 1 day after the end of the petition
            Actual time: 2 days after the end of the petition
        Expected case:
            1 mail is sent to each attendee
        """
        self._create_third_registration()
        new_end = self.petition_date_end + relativedelta(days=2)
        with freeze_time(new_end), self.mock_mail_gateway():
            self.petition_cron_id.method_direct_trigger()

        self.assertTrue(
            self.petition_next_scheduler.mail_sent,
            "petition: reminder scheduler should should have run",
        )
        self.assertTrue(
            self.petition_next_scheduler.done,
            "petition: reminder scheduler should have run",
        )

        self.assertEqual(
            len(self._new_mails),
            3,
            "petition: should have scheduled 3 mails, one for each registration",
        )
