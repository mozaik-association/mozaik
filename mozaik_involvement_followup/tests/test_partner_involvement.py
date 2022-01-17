# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests.common import SavepointCase


class TestPartnerInvolvement(SavepointCase):
    def setUp(self):
        super().setUp()

        self.user = self.env.ref("distribution_list.first_user")

        # Let the representative of the mandate be an Odoo user.
        self.mandate = self.env.ref("mozaik_mandate.intm_paul_regional")
        self.mandate.write({"partner_id": self.user.partner_id})

        self.assembly_instance = self.mandate.int_assembly_id.instance_id

        self.ic = self.env["partner.involvement.category"].create(
            {
                "name": "Wants to be recontacted",
                "nb_deadline_days": 15,
                "mandate_category_id": self.mandate.mandate_category_id.id,
            }
        )

    def test_create_involvement(self):
        """Creating a new involvement having self.ic as involvement category.
        We check that the follower was set, and that the activity was
        scheduled."""
        omar_sy = self.env["res.partner"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "int_instance_ids": [(5, 0), (4, self.assembly_instance.id)],
            }
        )
        involvement = self.env["partner.involvement"].create(
            {
                "partner_id": omar_sy.id,
                "involvement_category_id": self.ic.id,
            }
        )

        self.assertEqual(
            involvement.deadline,
            date.today() + relativedelta(days=15),
            "Deadline was not set correctly.",
        )
        self.assertEqual(len(involvement.message_follower_ids), 2)
        self.assertIn(
            "first partner user",
            involvement.message_follower_ids.mapped("name"),
            "Representative of the mandate was not set as a follower",
        )
        activity = involvement.activity_ids
        self.assertEqual(len(activity), 1)
        self.assertEqual(
            activity.note,
            "<p> Partner: Omar Sy </p> <p> Subject: Wants to be recontacted </p>",
        )
        self.assertEqual(activity.date_deadline, involvement.deadline)
        self.assertEqual(activity.user_id.name, "first partner user")
