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
from odoo.exceptions import ValidationError


class TestAddressAddress(TransactionCase):

    _module_ns = 'mozaik_address'

    def setUp(self):
        super().setUp()

        self.model_address = self.env['address.address']

    def test_create_address(self):
        vals = {
            'country_id': self.env.ref("base.be").id,
            'zip_man': '4100',
            'city_man': 'Seraing',
            'street_man': 'Rue de Colard Trouillet',
            'number': '7',
        }
        adr = self.model_address.create(vals)
        self.assertEqual(
            adr.name,
            'Rue de Colard Trouillet 7 - 4100 Seraing',
            'Create address fails with wrong name')
        self.assertEqual(
            adr.zip, '4100', 'Create address fails with wrong zip')
        self.assertEqual(
            adr.street,
            'Rue de Colard Trouillet 7',
            'Create address fails with wrong street')

        vals = {
            'number': '7',
            'box': False,
            'sequence': 3,
        }
        adr.write(vals)
        self.assertEqual(
            adr.name,
            'Rue de Colard Trouillet 7 [3] - 4100 Seraing',
            'Update address fails with wrong name')
        self.assertEqual(
            adr.street,
            'Rue de Colard Trouillet 7',
            'Update address fails with wrong street')

        vals = {
            'country_id': self.env.ref("base.us").id,
            'zip_man': '10017',
            'city_man': 'New York',
            'street_man': 'United Nations',
        }
        adr = self.model_address.create(vals)
        self.assertEqual(
            adr.name,
            'United Nations - New York - United States',
            'Create address fails with wrong name')
        self.assertEqual(
            adr.zip,
            '10017',
            'Create address fails with wrong zip')
        self.assertEqual(
            adr.street,
            'United Nations',
            'Create address fails with wrong street')

        # test the technical name
        vals = {
            'country_id': self.env.ref("base.be").id,
            'zip_man': '4100',
            'city_man': 'Seraing',
            'street_man': 'AAAAAàéÉçùièêÈ',
            'number': '7',
        }
        adr = self.model_address.create(vals)
        self.assertTrue(
            'aaaaaaeecuieee' in adr.technical_name,
            'No Accented char and no Upper For technical name')

    def test_copy_address(self):
        adr_3 = self.env.ref('%s.address_3' % self._module_ns)
        adr_4 = self.env.ref('%s.address_4' % self._module_ns)

        # 1/ an address with a null sequence cannot be duplicated
        self.assertRaises(ValidationError, adr_3.copy)

        # 2/ otherwise copy is allowed and the sequence is increased
        adr = adr_4.copy()
        self.assertEqual(
            adr.sequence, 2, 'Copy address fails with wrong sequence')
