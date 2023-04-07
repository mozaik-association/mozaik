# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestMembershipRequest(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.harry = cls.env["res.partner"].create({"name": "Harry Potter"})
        cls.ron = cls.env["res.partner"].create({"name": "Ron Weasley"})

    def setUp(self):
        super().setUp()
        self.sponsored_membership = self.env["product.template"].create(
            {
                "name": "Sponsored Membership",
                "membership": True,
                "categ_id": self.ref("mozaik_membership.membership_product_category"),
                "lst_price": 0,
                "advance_workflow_as_paid": True,
            }
        )
        self.product_sponsored = self.env["product.product"].search(
            [("product_tmpl_id.name", "=", "Sponsored Membership")], limit=1
        )
        self.sponsor_mt = self.env["membership.tarification"].create(
            {
                "name": "Sponsored Membership",
                "product_id": self.product_sponsored.id,
                "sequence": 0,
                "code": "membership_request"
                " and membership_request.sponsor_id"
                " and membership_request.can_be_sponsored",
            }
        )
        self.usual_subscription = self.env.ref(
            "mozaik_membership.membership_product_isolated"
        )
        self.usual_subscription.price = 20.0

    def test_membership_request_can_be_sponsored_new_partner(self):
        """
        Create a MR for a new partner.
        Check that can_be_sponsored is True
        """
        mr = self.env["membership.request"].create(
            {
                "lastname": "Granger",
                "firstname": "Hermione",
            }
        )
        self.assertTrue(mr.can_be_sponsored)

    def test_membership_request_sponsor_02(self):
        """
        Create a MR for Ron, with Harry as sponsor.
        Validate the request -> Harry is Ron's sponsor
        """
        mr = self.env["membership.request"].create(
            {
                "lastname": "Weasley",
                "firstname": "Ron",
                "partner_id": self.ron.id,
                "sponsor_id": self.harry.id,
            }
        )
        mr.validate_request()
        self.assertEqual(self.ron.sponsor_id, self.harry)

    def test_membership_request_cannot_be_sponsored_member(self):
        """
        Make Harry become a member and create a membership request for him.
        Check that can_be_sponsored is False
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.harry.int_instance_ids[0].id,
                "state_id": self.ref("mozaik_membership.member"),
            }
        ).action_add()
        self.assertEqual(self.harry.membership_state_code, "member")
        mr = self.env["membership.request"].create(
            {
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
            }
        )
        self.assertFalse(mr.can_be_sponsored)

    def test_membership_request_can_be_sponsored_former_member_no_sponsor(self):
        """
        Make Harry become a former member and create a membership request for him.
        Check that can_be_sponsored is True because he has no sponsor.
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.harry.int_instance_ids[0].id,
                "state_id": self.ref("mozaik_membership.former_member"),
            }
        ).action_add()
        self.assertEqual(self.harry.membership_state_code, "former_member")
        mr = self.env["membership.request"].create(
            {
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
            }
        )
        self.assertTrue(mr.can_be_sponsored)

    def test_membership_request_cannot_be_sponsored_former_member_sponsor(self):
        """
        Make Ron become Harry's sponsor.
        Make Harry become a former member and create a membership request for him.
        Check that can_be_sponsored is False because he has a sponsor.
        """
        self.harry.sponsor_id = self.ron
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.harry.int_instance_ids[0].id,
                "state_id": self.ref("mozaik_membership.former_member"),
            }
        ).action_add()
        self.assertEqual(self.harry.membership_state_code, "former_member")
        mr = self.env["membership.request"].create(
            {
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
            }
        )
        self.assertFalse(mr.can_be_sponsored)

    def test_free_membership_line_new_member(self):
        """
        Harry has no membership line yet.
        Create a MR of type 'm' for Harry, setting Ron as sponsor.
        Validate the request.
        Check that Harry became a member committee with a free membership.
        """
        # Assert that the sponsored membership tarification appears first
        mt = self.env["membership.tarification"].search([], limit=1)
        self.assertEqual(mt, self.sponsor_mt)

        mr = self.env["membership.request"].create(
            {
                "request_type": "m",
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
                "sponsor_id": self.ron.id,
            }
        )

        # Validate the request
        mr.write(
            mr._onchange_partner_id_vals(
                mr.is_company, mr.request_type, mr.partner_id.id, mr.technical_name
            )
        )
        mr.validate_request()

        # Harry has two membership lines: member candidate (free and paid, inactive)
        # and member committee (free and paid, active)
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
        self.assertTrue(active_line.is_sponsored)

        self.assertEqual(self.harry.sponsor_id, self.ron)

    def test_free_membership_line_member_candidate(self):
        """
        Make Harry become a member candidate first, with a non-free product.
        Create a MR of type 'm' for Harry, setting Ron as sponsor.
        Validate the request.
        Check that Harry's membership line was modified: the price is now 0 and
        the product is now the sponsored membership.
        Check that hence this ML was marked as paid and that Harry now has a second ML
        as member_committee.
        """
        wiz = self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.harry.int_instance_ids[0].id,
                "state_id": self.ref("mozaik_membership.member_candidate"),
                "product_id": self.usual_subscription.id,
                "price": self.usual_subscription.price,
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
                "sponsor_id": self.ron.id,
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
        self.assertEqual(not_active_line.product_id, self.product_sponsored)
        self.assertTrue(active_line.is_sponsored)

    def test_sponsored_membership_not_member_wants_to_pay(self):
        """
        Harry has no membership line yet.
        Create a MR of type 'm' for Harry, setting Ron as sponsor. But Harry wants to
        pay 8€ for his membership.
        Validate the request.
        Check that Harry became a member candidate with a sponsored membership product,
        but with his line price = 8€, not paid.
        """
        # Assert that the sponsored membership tarification appears first
        mt = self.env["membership.tarification"].search([], limit=1)
        self.assertEqual(mt, self.sponsor_mt)

        mr = self.env["membership.request"].create(
            {
                "request_type": "m",
                "lastname": "Potter",
                "firstname": "Harry",
                "partner_id": self.harry.id,
                "sponsor_id": self.ron.id,
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
        self.assertEqual(active_line.product_id, self.product_sponsored)
        self.assertTrue(active_line.is_sponsored)

        self.assertEqual(self.harry.sponsor_id, self.ron)
