# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestPartner(TransactionCase):

    def setUp(self):
        super().setUp()

        self.partner_obj = self.env['res.partner']
        self.ms_obj = self.env['membership.state']
        self.ml_obj = self.env['membership.line']
        self.prd_obj = self.env['product.template']
        self.imd_obj = self.env['ir.model.data']

        self.partner1 = self.env.ref(
            'mozaik_coordinate.res_partner_thierry')

        self.partner2 = self.env.ref(
            'mozaik_membership.res_partner_fgtb')

        self.user_model = self.env['res.users']
        self.partner_jacques_id = self.env.ref(
            'mozaik_coordinate.res_partner_jacques')
        self.tarification1 = self.env.ref(
            "mozaik_membership.membership_tarification_first_rule")
        self.tarification2 = self.env.ref(
            "mozaik_membership.membership_tarification_reduce_rule")
        self.tarification3 = self.env.ref(
            "mozaik_membership.membership_tarification_default_rule")

    def test_change_instance(self):
        '''
        Check that instance well updated into the partner when its main postal
        coo is changed
        '''
        postal_obj = self.env['postal.coordinate']
        address_obj = self.env['address.address']
        zip_obj = self.env['res.city']

        int_instance_id = self.ref('mozaik_structure.int_instance_01')

        postal_rec = postal_obj.search([], limit=1)
        partner = postal_rec.partner_id
        vals = {
            'zipcode': '123456789',
            'name': 'numbers',
            'country_id': self.ref("base.be"),
        }
        zipcode = zip_obj.create(vals)
        vals = {
            'country_id': self.ref("base.be"),
            'city_id': zipcode.id,
        }
        address = address_obj.create(vals)
        vals = {
            'address_id': address.id,
            'partner_id': partner.id,
            'is_main': True,
        }
        postal_rec = postal_obj.create(vals)
        # self.assertIn(
        #     int_instance_id, postal_rec.partner_id.int_instance_ids.ids)

    def test_create_user_from_partner(self):
        """
        Test the propagation of int_instance into the int_instance_m2m_ids
        when creating a user from a partner
        """
        jacques = self.partner_jacques_id
        user_model = self.user_model

        # Check for reference data
        dom = [('partner_id', '=', jacques.id)]
        user = user_model.search(dom)
        self.assertFalse(
            user, 'Wrong expected reference data for this test')

        # Create a user from a partner
        jacques._create_user('jack', self.env["res.groups"])
        # self.assertEqual(
        #     jacques.int_instance_id, jacques.int_instance_m2m_ids,
        #     'Update partner fails with wrong int_instance_m2m_ids')

    def test_compute_subscription_product_id(self):
        """
        Test the computation of the subscription_product_id who depends
        on rules set on membership.tarification.
        This test is based on rule set on demo directory
        :return:
        """
        partner = self.partner1
        membership_obj = self.env['membership.line']
        # Remove existing related membership.line
        # Match with tarification1
        partner.write({
            'membership_line_ids': [(6, False, [])],
        })
        partner.invalidate_cache()
        self.assertEqual(
            partner.subscription_product_id, self.tarification1.product_id)
        # Match with tarification2
        partner.write({
            'function': 'Software Developer',
        })
        instance = self.env['int.instance'].search([], limit=1, offset=1)
        values = membership_obj._build_membership_values(
            partner, instance)
        membership_obj.create(values)
        partner.invalidate_cache()
        self.assertEqual(
            partner.subscription_product_id, self.tarification2.product_id)
        # Match with tarification3
        partner.write({
            'function': 'I do not match',
        })
        partner.invalidate_cache()
        self.assertEqual(
            partner.subscription_product_id, self.tarification3.product_id)
        # If we remove membership lines, come-back to tarification1
        partner.write({
            'membership_line_ids': [(6, False, [])],
        })
        partner.invalidate_cache()
        self.assertEqual(
            partner.subscription_product_id, self.tarification1.product_id)
        # If we let membership lines empty and with a match on the second
        # tarification, we should stay on tarification1 due to the sequence
        partner.write({
            'function': 'Software Developer',
        })
        partner.invalidate_cache()
        self.assertEqual(
            partner.subscription_product_id, self.tarification1.product_id)
        # But if we update the sequence, the tarification2 is executed before
        # the tarification1
        self.tarification1.write({
            'sequence': self.tarification2.sequence + 1,
        })
        partner.write({
            'function': 'Software Developer',
        })
        partner.invalidate_cache()
        self.assertEqual(
            partner.subscription_product_id, self.tarification2.product_id)
        return
