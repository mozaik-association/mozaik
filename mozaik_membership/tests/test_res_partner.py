# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import TransactionCase


class TestPartner(TransactionCase):
    def setUp(self):
        super().setUp()

        self.partner1 = self.env.ref("mozaik_address.res_partner_thierry")
        self.partner_jacques_id = self.env.ref("mozaik_membership.res_partner_jacques")
        self.tarification1 = self.env.ref(
            "mozaik_membership.membership_tarification_first_rule"
        )
        self.tarification2 = self.env.ref(
            "mozaik_membership.membership_tarification_reduce_rule"
        )
        self.tarification3 = self.env.ref(
            "mozaik_membership.membership_tarification_default_rule"
        )
        self.member_state = self.env.ref("mozaik_membership.member")

    def test_create_user_from_partner(self):
        """
        Test the propagation of int_instance_ids into the int_instance_m2m_ids
        when creating a user from a partner
        """
        jacques = self.partner_jacques_id
        jacques.force_int_instance_id = jacques._default_force_int_instance_id()

        # Check for reference data: jacques is not a user
        self.assertFalse(jacques.user_ids)

        # Create a user from a partner
        jacques._create_user("jack", self.env["res.groups"])
        self.assertEqual(jacques.int_instance_ids, jacques.int_instance_m2m_ids)
        return

    def test_compute_subscription_product_id(self):
        """
        Test the computation of the subscription_product_id who depends
        on rules set on membership.tarification.
        This test is based on rule set on demo directory
        :return:
        """
        partner = self.partner1
        membership_obj = self.env["membership.line"]
        # Remove existing related membership.line
        # Match with tarification1
        default_instance = partner._default_force_int_instance_id()
        partner.write(
            {
                "membership_line_ids": [(6, False, [])],
                "force_int_instance_id": default_instance.id,
            }
        )
        partner.invalidate_cache()
        self.assertEqual(partner.subscription_product_id, self.tarification1.product_id)
        # Match with tarification2
        partner.write(
            {
                "function": "Software Developer",
            }
        )
        instance = self.env["int.instance"].search([], limit=1, offset=1)
        values = membership_obj._build_membership_values(
            partner, instance, self.member_state
        )
        membership_obj.create(values)
        partner.invalidate_cache()
        self.assertEqual(partner.subscription_product_id, self.tarification2.product_id)
        # Match with tarification3
        partner.write(
            {
                "function": "I do not match",
            }
        )
        partner.invalidate_cache()
        self.assertEqual(partner.subscription_product_id, self.tarification3.product_id)
        # If we remove membership lines, come-back to tarification1
        partner.write(
            {
                "membership_line_ids": [(6, False, [])],
                "force_int_instance_id": default_instance.id,
            }
        )
        partner.invalidate_cache()
        self.assertEqual(partner.subscription_product_id, self.tarification1.product_id)
        # If we let membership lines empty and with a match on the second
        # tarification, we should stay on tarification1 due to the sequence
        partner.write(
            {
                "function": "Software Developer",
            }
        )
        partner.invalidate_cache()
        self.assertEqual(partner.subscription_product_id, self.tarification1.product_id)
        # But if we update the sequence, the tarification2 is executed before
        # the tarification1
        self.tarification1.write(
            {
                "sequence": self.tarification2.sequence + 1,
            }
        )
        partner.write(
            {
                "function": "Software Developer",
            }
        )
        partner.invalidate_cache()
        self.assertEqual(partner.subscription_product_id, self.tarification2.product_id)
        return

    def test_resignation(self):
        """
        Test the resignation of a member, former_member or supporter.
        All of its opened membership must be closed.
        :return:
        """
        partner = self.partner1
        membership_obj = self.env["membership.line"]

        values = {
            "partner_id": partner.id,
            "date_from": fields.Date.from_string(fields.Date.today()),
        }
        vals = dict(
            values,
            int_instance_id=self.ref("mozaik_membership.int_instance_03"),
            state_id=self.ref("mozaik_membership.member"),
        )
        membership_obj.create(vals)
        vals = dict(
            values,
            int_instance_id=self.ref("mozaik_structure.int_instance_02"),
            state_id=self.ref("mozaik_membership.supporter"),
        )
        membership_obj.create(vals)
        # partner has now 3 opened membership lines
        self.assertEqual(
            2, len(partner.membership_line_ids.filtered(lambda s: s.active))
        )
        # and it is no longer 'without_membership'
        before_resignation_state_code = partner.membership_state_code
        self.assertNotEqual("without_membership", before_resignation_state_code)
        # resign it
        partner.action_resignation()
        # partner has now only 1 membership line
        opened_lines = partner.membership_line_ids.filtered(lambda s: s.active)
        self.assertEqual(1, len(opened_lines))
        # and it is excluded
        self.assertTrue(partner.is_excluded)
        # and its state has changed
        self.assertNotEqual(
            before_resignation_state_code, partner.membership_state_code
        )
        # resign it again
        partner.action_resignation()
        # collection of membership lines did not change
        self.assertEqual(
            opened_lines, partner.membership_line_ids.filtered(lambda s: s.active)
        )
        return
