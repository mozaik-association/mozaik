# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import SavepointCase


class TestFreeMembership(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.harry = cls.env["res.partner"].create({"name": "Harry Potter"})
        cls.ron = cls.env["res.partner"].create({"name": "Ron Weasley"})
        cls.free_membership = cls.env["product.template"].create(
            {
                "name": "Free Membership",
                "membership": True,
                "categ_id": cls.env.ref(
                    "mozaik_membership.membership_product_category"
                ).id,
                "lst_price": 0,
                "advance_workflow_as_paid": True,
            }
        )
        cls.subscription_free = cls.env["product.product"].search(
            [("product_tmpl_id.name", "=", "Free Membership")], limit=1
        )
        cls.free_mt = cls.env["membership.tarification"].create(
            {
                "name": "Free Membership",
                "product_id": cls.subscription_free.id,
                "sequence": 100,
                "code": "0 == 1",  # This tarification is only given on demand.
            }
        )
        cls.usual_subscription = cls.env.ref(
            "mozaik_membership.membership_product_isolated"
        )
        cls.usual_subscription.write({"list_price": 20.0})

    def test_free_membership_new_partner(self):
        """
        Create a MR for a partner having no ML, forcing the Free product
        Check that 2 membership lines were created:
        - A member candidate free line, inactive and paid
        - A member committee free line, active and paid
        """
        mr = self.env["membership.request"].create(
            {
                "request_type": "m",
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
                "force_product_id": self.subscription_free.id,
            }
        )
        mr.write(
            mr._onchange_partner_id_vals(
                mr.is_company, mr.request_type, mr.partner_id.id, mr.technical_name
            )
        )
        mr.validate_request()
        self.assertEqual(self.harry.membership_state_code, "member_committee")
        self.assertEqual(2, len(self.harry.membership_line_ids))
        active_line = self.harry.membership_line_ids.filtered("active")
        not_active_line = self.harry.membership_line_ids.filtered(
            lambda ml: not ml.active
        )
        self.assertTrue(active_line)
        self.assertTrue(not_active_line)
        self.assertEqual(active_line.state_id.code, "member_committee")
        self.assertEqual(not_active_line.state_id.code, "member_candidate")
        self.assertTrue(active_line.paid)
        self.assertTrue(not_active_line.paid)
        self.assertEqual(active_line.price, 0)
        self.assertEqual(not_active_line.price, 0)

    def test_free_membership_line_member_candidate(self):
        """
        Make Harry become a member candidate first, with a non-free product.
        Create a MR of type 'm' for Harry, forcing the free product.
        Validate the request.
        Check that Harry's membership line was modified: the price is now 0 and
        the product is now the free membership.
        Check that hence this ML was marked as paid and that Harry now has a second ML
        as member_committee.
        :return:
        """
        wiz = self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.harry.int_instance_ids[0].id,
                "state_id": self.ref("mozaik_membership.member_candidate"),
                "product_id": self.usual_subscription.id,
                "price": self.usual_subscription.list_price,
            }
        )
        wiz.action_add()
        self.assertEqual(self.harry.membership_state_code, "member_candidate")
        self.assertEqual(len(self.harry.membership_line_ids), 1)
        self.assertNotEqual(self.harry.membership_line_ids.price, 0)

        # Create the request
        mr = self.env["membership.request"].create(
            {
                "request_type": "m",
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
                "force_product_id": self.subscription_free.id,
            }
        )

        # Validate the request
        mr.write(
            mr._onchange_partner_id_vals(
                mr.is_company, mr.request_type, mr.partner_id.id, mr.technical_name
            )
        )
        mr.validate_request()

        self.assertEqual(len(self.harry.membership_line_ids), 2)
        active_line = self.harry.membership_line_ids.filtered("active")
        not_active_line = self.harry.membership_line_ids.filtered(
            lambda ml: not ml.active
        )
        self.assertTrue(active_line)
        self.assertTrue(not_active_line)
        self.assertEqual(active_line.state_id.code, "member_committee")
        self.assertEqual(not_active_line.state_id.code, "member_candidate")
        self.assertEqual(not_active_line.price, 0)
        self.assertEqual(not_active_line.product_id, self.subscription_free)

    def test_free_membership_not_member_wants_to_pay(self):
        """
        Harry has no membership line yet.
        Create a MR of type 'm' for Harry, forcing the free product. But Harry wants to
        pay 8€ for his membership.
        Validate the request.
        Check that Harry became a member candidate with a free membership product,
        but with his line price = 8€, not paid.
        """
        mr = self.env["membership.request"].create(
            {
                "request_type": "m",
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
                "force_product_id": self.subscription_free.id,
                "amount": 8,
            }
        )

        # Validate the request
        mr.write(
            mr._onchange_partner_id_vals(
                mr.is_company, mr.request_type, mr.partner_id.id, mr.technical_name
            )
        )
        mr.validate_request()

        # Harry has one membership lines: member candidate (not paid, active, 8€)
        self.assertEqual(self.harry.membership_state_code, "member_candidate")
        self.assertEqual(1, len(self.harry.membership_line_ids))
        active_line = self.harry.membership_line_ids.filtered("active")
        self.assertTrue(active_line)
        self.assertEqual(active_line.state_id.code, "member_candidate")
        self.assertFalse(active_line.paid)
        self.assertEqual(active_line.price, 8)
        self.assertEqual(active_line.product_id, self.subscription_free)

    def test_free_membership_already_member_candidate_wants_to_pay(self):
        """
        Make Harry become a member candidate first, with a non-free product.
        Create a MR of type 'm' for Harry, forcing the free product. But Harry wants to
        pay 8€ for his membership.
        Validate the request.
        Check that Harry's membership line was modified: the price is now 8 and
        the product is now the free membership. This ML is still active.
        """
        wiz = self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.harry.int_instance_ids[0].id,
                "state_id": self.ref("mozaik_membership.member_candidate"),
                "product_id": self.usual_subscription.id,
                "price": self.usual_subscription.list_price,
            }
        )
        wiz.action_add()
        self.assertEqual(self.harry.membership_state_code, "member_candidate")
        self.assertEqual(len(self.harry.membership_line_ids), 1)
        self.assertNotEqual(self.harry.membership_line_ids.price, 0)

        # Create the request
        mr = self.env["membership.request"].create(
            {
                "request_type": "m",
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
                "force_product_id": self.subscription_free.id,
                "amount": 8,
            }
        )

        # Validate the request
        mr.write(
            mr._onchange_partner_id_vals(
                mr.is_company, mr.request_type, mr.partner_id.id, mr.technical_name
            )
        )
        mr.validate_request()

        self.assertEqual(len(self.harry.membership_line_ids), 1)
        active_line = self.harry.membership_line_ids[0]
        self.assertEqual(active_line.state_id.code, "member_candidate")
        self.assertFalse(active_line.paid)
        self.assertEqual(active_line.price, 8)
        self.assertEqual(active_line.product_id, self.subscription_free)
