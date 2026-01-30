# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mozaik_event_membership_request_involvement.tests import (
    test_event_registration,
)


class TestEventRegistration(test_event_registration.TestEventRegistration):
    def test_membership_request_created(self):
        self.assertEqual(len(self.mr), 1)
        event_origin = self.env.ref(
            "mozaik_event_membership_request_origin.membership_request_origin_event"
        )
        self.assertEqual(self.mr.origin_id.id, event_origin.id)
