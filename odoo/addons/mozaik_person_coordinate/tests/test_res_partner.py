# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from anybox.testing.openerp import SharedSetupTransactionCase


class test_res_partner(SharedSetupTransactionCase):

    _module_ns = 'mozaik_person_coordinate'

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
