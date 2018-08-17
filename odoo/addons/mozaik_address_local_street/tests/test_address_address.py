##############################################################################
#
#     This file is part of mozaik_address, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_address is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_address is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_address.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo.tests.common import TransactionCase


class TestAddressAddress(TransactionCase):

    def setUp(self):
        super().setUp()

        self.model_address = self.env['address.address']

    def test_create_address(self):

        vals = {
            'country_id':
                self.env.ref("base.be").id,
            'city_id':
                self.env.ref("mozaik_address.res_city_1").id,
            'address_local_street_id':
                self.env.ref("mozaik_address_local_street.local_street_1").id,
            'box': '4b',
        }
        adr = self.model_address.create(vals)
        self.assertEqual(
            adr.name,
            'Grand-Place -/4b - 4500 Huy',
            'Create address fails with wrong name')
        self.assertEqual(
            adr.zip,
            '4500',
            'Create address fails with wrong zip')
        self.assertEqual(
            adr.street,
            'Grand-Place -/4b',
            'Create address fails with wrong street')
