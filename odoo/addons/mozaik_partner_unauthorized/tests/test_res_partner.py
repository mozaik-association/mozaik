# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):

    def setUp(self):
        super(test_res_partner, self).setUp()
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.partner_obj = self.env['res.partner']
        self.email_coordinate_obj = self.env['email.coordinate']

    def test_unauthorized(self):
        vals = {
            'name': 'Partner For The Unauthorized test',
        }
        partner = self.partner_obj.create(vals)
        self.assertFalse(
            partner.unauthorized,
            'With no coordinate: should not be unauthorized')
        vals = {
            'email': 'test@test.be',
            'partner_id': partner.id,
            'is_main': False
        }
        email_coordinate = self.email_coordinate_obj.create(vals)
        self.assertFalse(
            partner.unauthorized,
            'With a coordinate authorized: should not be unauthorized')
        email_coordinate.unauthorized = True
        self.assertTrue(
            partner.unauthorized,
            'With a coordinate unauthorized: should be unauthorized')
        email_coordinate.action_invalidate()
        self.assertFalse(
            partner.unauthorized,
            'With a coordinate unauthorized inactive: should not '
            'be unauthorized')
