# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from ..tests.common import TestPetitionCommon


class TestImmediateScheduler(TestPetitionCommon):
    def setUp(self):
        super().setUp()
        self._create_registrations()

    def test_registration_state(self):
        """
        Data:
            2 registrations
        Test case:
            date_open has to be equal to registration date (that is today)
        """
        self.assertTrue(
            all(reg.date_open == self.today for reg in self.reg1 + self.reg2),
            "Registrations: should have open date set to today",
        )

    def test_auto_executed_after_each_registration(self):
        """
        Data:
            2 registrations
            A scheduler set immediately after signature
        Test case:
            scheduler should have been executed after each registration
        Expected result:
            Mails are scheduled for today, and sent.
        """
        self.assertEqual(
            len(self.after_sub_scheduler.mail_registration_ids),
            2,
            "petition: should have 2 scheduled communication (1 / registration)",
        )
        for mail_registration in self.after_sub_scheduler.mail_registration_ids:
            self.assertEqual(mail_registration.scheduled_date, self.today)
            self.assertTrue(
                mail_registration.mail_sent,
                "petition: registration mail should be sent at registration creation",
            )

        self.assertTrue(
            self.after_sub_scheduler.done,
            "petition: all subscription mails should have been sent",
        )

    def test_mails_effectively_sent(self):
        """
        Data:
            2 registrations
            A scheduler set immediately after signature
        Test case:
            Check that the mails for both registrations are effectively sent
        """
        self.assertEqual(
            len(self._new_mails),
            2,
            "petition: should have 2 scheduled emails (1 / registration)",
        )

    def test_auto_execution_after_new_registration(self):
        """
        Data:
            2 old registrations, with mails already sent
        Test case:
            When creating a new registration, the subscription
            scheduler has to be auto-executed
        """
        self._create_third_registration()
        today_start = self.petition_date_begin + relativedelta(days=-1)
        self.assertEqual(
            len(self.after_sub_scheduler.mail_registration_ids),
            3,
            "petition: should have 3 scheduled communication (1 / registration)",
        )
        new_mail_reg = self.after_sub_scheduler.mail_registration_ids.filtered(
            lambda mail_reg: mail_reg.registration_id == self.reg3
        )
        self.assertEqual(new_mail_reg.scheduled_date, today_start)
        self.assertTrue(
            new_mail_reg.mail_sent,
            "petition: registration mail should be sent at registration creation",
        )
        self.assertTrue(
            self.after_sub_scheduler.done,
            "petition: all subscription mails should have been sent",
        )
