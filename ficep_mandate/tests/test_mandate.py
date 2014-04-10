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
import logging
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.osv import orm

_logger = logging.getLogger(__name__)


class test_mandate(SharedSetupTransactionCase):

    _data_files = (
        #'../../ficep_structure/tests/data/structure_data.xml',
    )

    _module_ns = 'ficep_mandate'

    def setUp(self):
        super(test_mandate, self).setUp()

    def test_duplicate_mandate_category(self):
        '''
            Test unique name of mandate category
        '''
        int_power_level_01_id = self.ref('ficep_structure.int_power_level_01')
        int_power_level_02_id = self.ref('ficep_structure.int_power_level_02')

        data = dict(name='category_01', int_power_level_id=int_power_level_01_id)
        self.registry('mandate.category').create(self.cr, self.uid, data)
        data['int_power_level_id'] = int_power_level_02_id
        self.assertRaises(orm.except_orm, self.registry('mandate.category').create, self.cr, self.uid, data)
