# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mozaik_event_membership_request_involvement.tests.test_event_registration import (  # noqa: B950 pylint: disable=line-too-long
    TestEventRegistration as BaseTestEventRegistration,
)


class TestEventRegistration(BaseTestEventRegistration):
    def test_registration_no_autovalidation(self):
        """
        Membership request is still in confirm.
        """
        self.event.auto_accept_membership = False
        self.env["event.registration"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@example.com",
                "event_id": self.event.id,
            }
        )
        mr = self._search_mr_linked_to_registration(
            lastname="Sy", firstname="Omar", email="omarsy@example.com"
        )
        self.assertEqual(len(mr), 1)
        self.assertEqual(mr.state, "confirm")

    def test_registration_complete_autovalidation(self):
        """
        Complete autovalidation case
        """
        self.event.write(
            {
                "auto_accept_membership": True,
                "autovalidation_type": "complete",
            }
        )
        self.env["event.registration"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@example.com",
                "event_id": self.event.id,
            }
        )
        mr = self._search_mr_linked_to_registration(
            lastname="Sy",
            firstname="Omar",
            email="omarsy@example.com",
            active=False,
        )
        self.assertEqual(len(mr), 1)
        self.assertEqual(mr.state, "validate")

    def test_registration_light_autovalidation(self):
        self.event.write(
            {
                "auto_accept_membership": True,
                "autovalidation_type": "light",
            }
        )
        self.env["event.registration"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@example.com",
                "event_id": self.event.id,
            }
        )
        mr = self._search_mr_linked_to_registration(
            lastname="Sy",
            firstname="Omar",
            email="omarsy@example.com",
            active=False,
        )
        self.assertEqual(len(mr), 2)
        self.assertEqual(set(mr.mapped("state")), {"validate", "light_autoval"})
