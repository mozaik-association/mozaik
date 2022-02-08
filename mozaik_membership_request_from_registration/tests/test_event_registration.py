# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestEventRegistration(TransactionCase):
    def test_event_registration_from_partner(self):
        event = self.env["event.event"].create(
            {
                "name": "Test event",
                "date_begin": datetime(2022, 1, 1, 8, 0, 0),
                "date_end": datetime(2022, 1, 1, 18, 0, 0),
            }
        )
        partner = self.env["res.partner"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "o.s@test.com",
                "phone": "043601234",
                "mobile": "0479123456",
            }
        )

        reg = self.env["event.registration"].create(
            {
                "event_id": event.id,
                "associated_partner_id": partner.id,
            }
        )

        reg._onchange_associated_partner_id()
        self.assertEqual(reg.lastname, partner.lastname)
        self.assertEqual(reg.firstname, partner.firstname)
        self.assertEqual(reg.email, partner.email)
        self.assertEqual(reg.phone, partner.phone)
        self.assertEqual(reg.mobile, partner.mobile)
