# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestEventEvent(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_post_init_hook(self):
        """
        Due to post_init_hook, there should exist one involvement category
        for each Event. We check that it is the case.
        """
        event_ids = self.env["event.event"].search([]).mapped("id")
        event_ids_from_involvement_categories = (
            self.env["partner.involvement.category"]
            .search([("event_id", "!=", False)])
            .mapped("event_id.id")
        )
        self.assertEqual(
            set(event_ids),
            set(event_ids_from_involvement_categories),
            "Each event should have an associated involvement category.",
        )
