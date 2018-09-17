# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import uuid
from datetime import date

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
            'int_instance_id': int_instance_id,
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
        self.assertEqual(
            int_instance_id, postal_rec.partner_id.int_instance_id.id)

    def test_generate_membership_reference(self):
        """
        Check if the membership reference match the arbitrary pattern:
          'MS: YYYY/<partner-id>'
        """
        p_obj = self.partner_obj
        # create a partner
        partner = p_obj.create(
            {'lastname': '%s' % uuid.uuid4()})
        year = str(date.today().year)
        # generate the reference
        genref = partner._generate_membership_reference(year)

        ref = 'MS: %s/%s' % (year, partner.id)
        self.assertEqual(genref, ref)

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
        self.assertEqual(
            jacques.int_instance_id, jacques.int_instance_m2m_ids,
            'Update partner fails with wrong int_instance_m2m_ids')
