# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mozaik_petition_membership_request_involvement.tests import (
    test_petition_registration,
)


class TestPetitionRegistration(test_petition_registration.TestEventRegistration):
    def test_membership_request_created(self):
        self.assertEqual(len(self.mr), 1)
        petition_origin = self.env.ref(
            "mozaik_petition_membership_request_origin.membership_request_origin_petition"
        )
        self.assertEqual(self.mr.origin_id.id, petition_origin.id)
