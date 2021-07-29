# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestIntInstance(TransactionCase):
    """
    Tests for int.instance
    """

    def setUp(self):
        super(TestIntInstance, self).setUp()
        self.membership_obj = self.env['membership.line']
        self.partner_obj = self.env['res.partner']
        self.instance = self.env.ref("mozaik_membership.int_instance_03")
        self.pricelist = self.env.ref(
            "mozaik_subscription_price.product_pricelist_instance")
        self.pricelist_item = self.env.ref(
            "mozaik_subscription_price.product_pricelist_instance_item1")
        self.instance.write({
            'product_pricelist_id': self.pricelist.id,
        })
        self.partner_marc = self.env.ref("mozaik_coordinate.res_partner_marc")
        self.product_free = self.env.ref(
            "mozaik_membership.membership_product_free")

    def test_check_number_int_instance(self):
        """
        Test the constrain _check_number_int_instance to ensure only 1
        int.instance (max) is related to the pricelist
        :return:
        """
        original_instance = self.instance
        duplicate_instance = original_instance.copy({
            'name': str(uuid4()),
            'code': '101',
        })
        pricelist = original_instance.product_pricelist_id
        # part of error message raised
        message = "These price lists are already linked to Internal Instances"
        # Test during write
        with self.assertRaises(exceptions.ValidationError) as e:
            duplicate_instance.write({
                'product_pricelist_id': pricelist.id,
            })
        self.assertIn(message, e.exception.name)
        # Test during copy
        with self.assertRaises(exceptions.ValidationError) as e:
            original_instance.copy({
                'product_pricelist_id': pricelist.id,
                'name': str(uuid4()),
                'code': '110',
            })
        self.assertIn(message, e.exception.name)
        # Test during create
        with self.assertRaises(exceptions.ValidationError) as e:
            original_instance.copy({
                'name': str(uuid4()),
                'product_pricelist_id': pricelist.id,
                'code': '111',
            })
        self.assertIn(message, e.exception.name)
