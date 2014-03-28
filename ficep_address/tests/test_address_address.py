# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_address_address(SharedSetupTransactionCase):

    _data_files = ('data/reference_data.xml',
                  )

    _module_ns = 'ficep_address'

    def setUp(self):
        super(test_address_address, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.model_address = self.registry('address.address')

    def test_create_address(self):
        cr, uid = self.cr, self.uid
        dic = {
            'country_id': self.ref("base.be"),
            'zip_man': '4100',
            'town_man': 'Seraing',
            'street_man': 'Rue de Colard Trouillet',
            'number': '7',
        }
        adr_id = self.model_address.create(cr, uid, dic)
        adr = self.model_address.browse(cr, uid, [adr_id])[0]
        self.assertEqual(adr.name, '7 Rue de Colard Trouillet - 4100 Seraing', 'Create address fails with wrong name')
        self.assertEqual(adr.zip, '4100', 'Create address fails with wrong zip')
        self.assertEqual(adr.street, '7 Rue de Colard Trouillet', 'Create address fails with wrong street')

        dic = {
            'country_id': self.ref("base.be"),
            'address_local_zip_id': self.ref("ficep_address.local_zip_1"),
            'address_local_street_id': self.ref("ficep_address.local_street_1"),
            'box': '4b',
        }
        adr_id = self.model_address.create(cr, uid, dic)
        adr = self.model_address.browse(cr, uid, [adr_id])[0]
        self.assertEqual(adr.name, '-/4b Grand-Place - 4500 Huy', 'Create address fails with wrong name')
        self.assertEqual(adr.zip, '4500', 'Create address fails with wrong zip')
        self.assertEqual(adr.street, '-/4b Grand-Place', 'Create address fails with wrong street')

        dic = {
            'number': '7',
            'box': False,
            'sequence': 3,
        }
        self.model_address.write(cr, uid, adr_id, dic)
        adr = self.model_address.browse(cr, uid, [adr_id])[0]
        self.assertEqual(adr.name, '[3]: 7 Grand-Place - 4500 Huy', 'Update address fails with wrong name')
        self.assertEqual(adr.street, '7 Grand-Place', 'Update address fails with wrong street')

        dic = {
            'country_id': self.ref("base.us"),
            'zip_man': '10017',
            'town_man': 'New York',
            'street_man': 'United Nations',
        }
        adr_id = self.model_address.create(cr, uid, dic)
        adr = self.model_address.browse(cr, uid, [adr_id])[0]
        self.assertEqual(adr.name, 'United Nations - New York - United States', 'Create address fails with wrong name')
        self.assertEqual(adr.zip, '10017', 'Create address fails with wrong zip')
        self.assertEqual(adr.street, 'United Nations', 'Create address fails with wrong street')

        #test the technical name
        dic = {
            'country_id': self.ref("base.be"),
            'zip_man': '4100',
            'town_man': 'Seraing',
            'street_man': 'AAAAAéÉçùièêÈ',
            'number': '7',
        }
        adr_id = self.model_address.create(cr, uid, dic)
        adr = self.model_address.browse(cr, uid, [adr_id])[0]
        self.assertTrue('aaaaaeecuieee' in adr.technical_name, 'No Accented char and no Upper For technical name')

    def test_copy_address(self):
        cr, uid = self.cr, self.uid
        adr_3 = self.ref('%s.address_3' % self._module_ns)
        adr_4 = self.ref('%s.address_4' % self._module_ns)

        # 1/ an address with a null sequence cannot be duplicated
        self.assertRaises(orm.except_orm, self.model_address.copy, cr, uid, adr_3)

        # 2/ otherwise copy is allowed and the sequence is increased
        adr_id = self.model_address.copy(cr, uid, adr_4)
        adr = self.model_address.browse(cr, uid, [adr_id])[0]
        self.assertEqual(adr.sequence, 2, 'Copy address fails with wrong sequence')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
