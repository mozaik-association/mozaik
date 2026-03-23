# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.event.tests.common import TestEventCommon
from odoo.addons.mail.tests.common import MockEmail


class TestMailSchedule(TestEventCommon, MockEmail):
    def test_event_counter_registration(self):
        # deactivate other schedulers to avoid messing with crons
        self.env["event.mail"].search([]).unlink()

        now = datetime(2021, 3, 20, 14, 30, 15)
        event_date_begin = datetime(2021, 3, 22, 8, 0, 0)
        event_date_end = datetime(2021, 3, 24, 18, 0, 0)

        test_event = (
            self.env["event.event"]
            .with_user(self.user_eventmanager)
            .create(
                {
                    "name": "TestEventMail",
                    "date_begin": event_date_begin,
                    "date_end": event_date_end,
                    "event_mail_ids": [
                        (
                            0,
                            0,
                            {  # right at subscription
                                "interval_unit": "now",
                                "interval_type": "after_sub",
                                "template_id": self.env[
                                    "ir.model.data"
                                ].xmlid_to_res_id("event.event_subscription"),
                            },
                        ),
                    ],
                }
            )
        )

        after_sub_scheduler = self.env["event.mail"].search(
            [
                ("event_id", "=", test_event.id),
                ("interval_type", "=", "after_sub"),
                ("interval_unit", "=", "now"),
            ]
        )

        registration = self.env["event.registration"].create(
            {
                "create_date": now,
                "event_id": test_event.id,
                "name": "Reg1",
                "email": "reg1@example.com",
                "is_counter_registration": True,
            }
        )
        self.assertEqual(len(after_sub_scheduler.mail_registration_ids), 0)
        with self.mock_mail_gateway():
            registration.action_confirm()
        self.assertEqual(len(after_sub_scheduler.mail_registration_ids), 1)
        self.assertTrue(after_sub_scheduler.mail_registration_ids.mail_sent)
        self.assertTrue(after_sub_scheduler.done)
        self.assertEqual(len(self._new_mails), 0)
        self.assertEqual(registration.state, "done")
