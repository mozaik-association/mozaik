# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import SavepointCase


class TestMembershipLine(SavepointCase):
    """
    Tests for membership.line
    """

    def setUp(self):
        super(TestMembershipLine, self).setUp()
        self.membership_obj = self.env['membership.line']
        self.pseudo_state = self.browse_ref('mozaik_membership.member')
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

    def test_get_subscription_price1(self):
        """
        Test the _get_subscription price with a pricelist on the instance
        :return:
        """
        membership_obj = self.membership_obj
        # Patch method to force using another product
        partner = self.partner_marc
        instance = self.instance
        prices = [
            1256.369,
            1,
            10,
            36985.25,
        ]
        product = self.browse_ref('mozaik_membership.membership_product_free')
        self.assertEqual(self.pricelist_item.product_id, product)
        self.assertEqual(
            instance.product_pricelist_id, self.pricelist_item.pricelist_id)
        precision = membership_obj._fields.get('price').digits[1]
        for price in prices:
            self.pricelist_item.write({
                'fixed_price': price,
            })
            # No api.depends on the compute function so we have to invalidate
            # manually to force re-compute price field
            product.invalidate_cache()
            # For this test, ensure we use the same product
            # Use the precision defined on the price field
            result_price = membership_obj._build_membership_values(
                partner, instance, self.pseudo_state,
                product=product).get('price')
            self.assertAlmostEqual(price, result_price, places=precision)

    def test_get_subscription_price2(self):
        """
        Test the _get_subscription price without pricelist on the instance
        :return:
        """
        membership_obj = self.membership_obj
        # Patch method to force using another product
        partner = self.partner_marc
        instance = self.instance
        # Remove the pricelist for this test
        instance.write({
            'product_pricelist_id': False,
        })
        prices = [
            1256.369,
            1,
            10,
            36985.25,
        ]
        product = partner.subscription_product_id
        real_price = 55.36
        product.write({
            'list_price': real_price,
        })
        # Force to use this product
        self.pricelist_item.write({
            'product_id': product.id,
        })
        self.assertEqual(self.pricelist_item.product_id, product)
        precision = membership_obj._fields.get('price').digits[1]
        for price in prices:
            self.pricelist_item.write({
                'fixed_price': price,
            })
            # No api.depends on the compute function so we have to invalidate
            # manually to force re-compute price field
            product.invalidate_cache()
            # For this test, ensure we use the same product
            # Use the precision defined on the price field
            result_price = membership_obj._build_membership_values(
                partner, instance, self.pseudo_state).get('price')
            self.assertAlmostEqual(real_price, result_price, places=precision)
