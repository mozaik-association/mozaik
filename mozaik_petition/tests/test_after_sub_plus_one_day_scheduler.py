# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tools import formataddr

from ..tests.common import TestPetitionCommon


class TestAfterSubPlusOneDayScheduler(TestPetitionCommon):
    def setUp(self):
        super().setUp()
        self._create_registrations()

    def test_mails_scheduled_not_sent(self):
        """
        Data:
            A scheduler scheduled 1 day after the subscription
            2 registrations
        Test case:
            mails from scheduler are scheduled but not sent
        """
        self.assertEqual(
            len(self.after_sub_scheduler_2.mail_registration_ids),
            2,
            "petition: should have 2 scheduled communication (1 / registration)",
        )
        for mail_registration in self.after_sub_scheduler_2.mail_registration_ids:
            self.assertEqual(
                mail_registration.scheduled_date, self.today + relativedelta(days=1)
            )
            self.assertFalse(
                mail_registration.mail_sent,
                "petition: registration mail should be scheduled, not sent",
            )
        self.assertFalse(
            self.after_sub_scheduler_2.done,
            "petition: all subscription mails should be scheduled, not sent",
        )

    def test_scheduler_run_before_scheduled_date(self):
        """
        Data:
            A scheduler scheduled 1 day after the subscription
            2 registrations
        Test case:
            If scheduler run explicitly before scheduled date -> should not do anything
        """
        with freeze_time(self.today), self.mock_mail_gateway():
            self.after_sub_scheduler_2.execute()
        self.assertFalse(
            any(
                mail_reg.mail_sent
                for mail_reg in self.after_sub_scheduler_2.mail_registration_ids
            )
        )
        self.assertFalse(self.after_sub_scheduler_2.done)
        self.assertEqual(
            len(self._new_mails),
            0,
            "petition: should not send mails before scheduled date",
        )

    def test_scheduler_run_at_scheduled_date(self):
        """
        Data:
            A scheduler scheduled 1 day after the subscription
            2 registrations
        Test case:
            If scheduler run explicitly at scheduled date -> should send mails
        """

        today_registration = self.today + relativedelta(days=1)
        with freeze_time(today_registration), self.mock_mail_gateway():
            self.after_sub_scheduler_2.execute()

        # verify that subscription scheduler was auto-executed after each registration
        self.assertEqual(
            len(self.after_sub_scheduler_2.mail_registration_ids),
            2,
            "petition: should have 2 scheduled communication (1 / registration)",
        )
        self.assertTrue(
            all(
                mail_reg.mail_sent
                for mail_reg in self.after_sub_scheduler_2.mail_registration_ids
            )
        )
        self.assertTrue(
            self.after_sub_scheduler_2.done,
            "petition: all subscription mails should have been sent",
        )

        # check emails effectively sent
        self.assertEqual(
            len(self._new_mails),
            2,
            "petition: should have 2 scheduled emails (1 / registration)",
        )
        self.assertMailMailWEmails(
            [
                formataddr((self.reg1.lastname, self.reg1.email)),
                formataddr((self.reg2.lastname, self.reg2.email)),
            ],
            "outgoing",
            content=None,
            fields_values={
                "subject": "Your registration at %s" % self.test_petition.title,
                "email_from": self.user_petitionmanager.company_id.email_formatted,
            },
        )

    def test_auto_execution_after_new_registration(self):
        """
        Data:
            A scheduler scheduled 1 day after the subscription
            2 registrations with mails already sent
        Test case:
            When creating a new registration, its communication is scheduled
        """
        self._create_third_registration()
        today_start = self.petition_date_begin + relativedelta(days=-1)
        # verify that subscription scheduler was auto-executed after new registration
        self.assertEqual(
            len(self.after_sub_scheduler_2.mail_registration_ids),
            3,
            "petition: should have 3 scheduled communication (1 / registration)",
        )
        new_mail_reg = self.after_sub_scheduler_2.mail_registration_ids.filtered(
            lambda mail_reg: mail_reg.registration_id == self.reg3
        )
        self.assertEqual(
            new_mail_reg.scheduled_date, today_start + relativedelta(days=1)
        )

        today_registration = self.petition_date_begin
        with freeze_time(today_registration), self.mock_mail_gateway():
            self.after_sub_scheduler_2.execute()

        self.assertTrue(
            new_mail_reg.mail_sent,
            "petition: registration mail should be sent at scheduled date",
        )
        self.assertTrue(
            self.after_sub_scheduler_2.done,
            "petition: all subscription mails should have been sent",
        )
        self.assertEqual(
            len(self._new_mails),
            1,
            "petition: should have 1 scheduled emails (new registration only)",
        )
