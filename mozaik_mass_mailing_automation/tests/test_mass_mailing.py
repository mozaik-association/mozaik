# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestMassMailing(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cron_id = cls.env.ref("mass_mailing.ir_cron_mass_mailing_queue")

        # deactivate other mass mailings to avoid messing with crons
        cls.env["mailing.mailing"].search([]).unlink()

    def setUp(self):
        super().setUp()
        self.mailing_list_model = self.env["ir.model"].search(
            [("model", "=", "mailing.list")], limit=1
        )
        self.mailing_list = self.env["mailing.list"].create(
            {
                "name": "List1",
                "contact_ids": [
                    (0, 0, {"name": "Fleurus", "email": "fleurus@example.com"}),
                    (0, 0, {"name": "Gorramts", "email": "gorramts@example.com"}),
                    (0, 0, {"name": "Ybrant", "email": "ybrant@example.com"}),
                ],
            }
        )

        self.creation_time = datetime(2021, 9, 16, 14, 23, 55)
        with freeze_time(self.creation_time):
            self.mailing = (self.env["mailing.mailing"]).create(
                {
                    "subject": "Automated mass mailing",
                    "mailing_model_id": self.mailing_list_model.id,
                    "automation": True,
                    "next_execution": self.creation_time,
                    "contact_list_ids": [(6, 0, self.mailing_list.ids)],
                }
            )

    def test_executable_automated_mailing(self):
        """
        Data (defined in setUp):
            self.mailing, a mass mailing with a list of 3 contacts
            and automation set to True
        Test case:
            - When executing the cron, mails are sent
            and next_execution is scheduled for the next day.
            - Adding a contact does not affect the mass mailing
            when done before next_execution.
            - Running the cron next day sends the mail to the new contact.
        """
        self.assertEqual(
            self.mailing.next_execution,
            self.creation_time,
            "Next execution should be set to creation time.",
        )
        now = self.creation_time + relativedelta(minutes=1)
        self.assertEqual(self.mailing.state, "draft", "State should be equal to draft.")
        self.mailing.action_put_in_queue()
        self.assertEqual(
            self.mailing.state, "in_queue", "State should now be equal to in_queue."
        )

        with freeze_time(now):
            self.cron_id.method_direct_trigger()
        self.assertEqual(
            self.mailing.state, "done", "State should now be equal to done."
        )
        self.assertEqual(
            self.mailing.sent,
            len(self.mailing_list.contact_ids),
            "All mails should have been sent.",
        )
        self.assertEqual(
            self.mailing.next_execution,
            self.creation_time + relativedelta(days=1),
            "Next execution is planned 24 hours later.",
        )

        # Adding a person to the mailing list, 1h10 after the cron sent the mail.
        now += relativedelta(hours=1, minutes=10)
        self.mailing_list.write(
            {"contact_ids": [(0, 0, {"name": "Dupont", "email": "dupont@example.com"})]}
        )
        self.assertEqual(
            len(self.mailing.contact_list_ids.contact_ids),
            4,
            "Error while adding a person to the mailing list.",
        )

        # executing cron before next_execution scheduled time -> nothing happens
        with freeze_time(now):
            self.cron_id.method_direct_trigger()
        self.assertEqual(
            self.mailing.sent,
            len(self.mailing_list.contact_ids) - 1,
            "The last email should not have been sent yet.",
        )

        # going after the next_execution scheduled time -> the last mail will be sent
        tomorrow = self.creation_time + relativedelta(hours=25)

        with freeze_time(tomorrow):
            self.cron_id.method_direct_trigger()
        self.assertEqual(
            self.mailing.state, "done", "State should now be equal to done."
        )
        self.assertEqual(
            self.mailing.sent,
            len(self.mailing_list.contact_ids),
            "The last email should have been sent.",
        )
        self.assertEqual(
            self.mailing.next_execution,
            self.creation_time + relativedelta(days=2),
            "Next execution is planned 24 hours later.",
        )

    def test_mass_mailing_before_next_execution(self):
        """
        Data (defined in the function):
            self.mailing2: a mass mailing whose next_execution is tomorrow
            and with automation set to True
        Test case:
            No mail is sent since next_execution is only tomorrow.
        """
        with freeze_time(self.creation_time):
            self.mailing2 = (self.env["mailing.mailing"]).create(
                {
                    "subject": "Second mass mailing",
                    "mailing_model_id": self.mailing_list_model.id,
                    "automation": True,
                    "next_execution": self.creation_time + relativedelta(days=1),
                    "contact_list_ids": [(6, 0, self.mailing_list.ids)],
                }
            )

        self.assertEqual(
            self.mailing2.next_execution,
            self.creation_time + relativedelta(days=1),
            "Next execution should be set to one day after creation time.",
        )
        now = self.creation_time + relativedelta(minutes=1)
        self.mailing2.action_put_in_queue()

        with freeze_time(now):
            self.cron_id.method_direct_trigger()
        self.assertEqual(
            self.mailing2.state, "in_queue", "Mass mailing should stay in queue."
        )
        self.assertEqual(self.mailing2.sent, 0, "No mail should have been sent.")
        self.assertEqual(
            self.mailing2.next_execution,
            self.creation_time + relativedelta(days=1),
            "Next execution did not change.",
        )

    def test_mass_mailing_without_automation(self):
        """
        Data (defined in the function):
            self.mailing3: a mass mailing with no automation process
        Test case:
            Field schedule_date is set to False for self.mailing3.
        """
        self.mailing3 = (self.env["mailing.mailing"]).create(
            {
                "subject": "Third mass mailing",
                "mailing_model_id": self.mailing_list_model.id,
                "automation": False,
                "contact_list_ids": [(6, 0, self.mailing_list.ids)],
            }
        )
        self.assertEqual(self.mailing3.schedule_date, False)

    def test_mass_mailing_removing_automation(self):
        """
        Data (defined in setUp):
            self.mailing: a mass mailing with an automation process
        Test case:
            schedule_date is set to be equal to next_execution.
            When cancelling the automation process, schedule_date becomes False.
        """
        self.assertEqual(self.mailing.schedule_date, self.mailing.next_execution)
        self.mailing.write({"automation": False})
        self.assertEqual(self.mailing.schedule_date, False)

    def test_cannot_create_automation_with_mailing_contact(self):
        """
        Test case:
            Create a mass mailing on mailing.contact and try to add
            an automation process.
            -> Forbidden by a constraint check.
        """
        mailing_contact_model = self.env["ir.model"].search(
            [("model", "=", "mailing.contact")], limit=1
        )
        mass_mailing = self.env["mailing.mailing"].create(
            {
                "subject": "Fourth mass mailing",
                "mailing_model_id": mailing_contact_model.id,
            }
        )
        with self.assertRaises(ValidationError):
            mass_mailing.write(
                {
                    "automation": True,
                    "next_execution": self.creation_time + relativedelta(days=1),
                }
            )
