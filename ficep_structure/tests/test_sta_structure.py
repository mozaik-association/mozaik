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
from openerp.addons.ficep_base.tests.test_abstract_ficep import abstract_ficep
from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase
import logging
_logger = logging.getLogger(__name__)


class test_sta_structure(abstract_ficep, SharedSetupTransactionCase):
    _data_files = ('../../ficep_structure/tests/data/structure_data.xml',
                   'data/structure_data.xml',
                  )

    _module_ns = 'ficep_structure'

    def setUp(self):
        super(test_sta_structure, self).setUp()
        self.model_abstract = self.registry('sta.power.level')
        self.invalidate_success_ids = [self.ref('%s.sta_power_level_10' % self._module_ns)]
        self.invalidate_fail_ids = [self.ref('%s.sta_power_level_01' % self._module_ns)]
        self.validate_ids = [self.ref('%s.sta_power_level_10' % self._module_ns)]

    def test_sta_assembly_consistence(self):
        '''
            Cannot create an assembly with a category and an instance of different power level
        '''
        assembly_category_id = self.ref('%s.sta_assembly_category_06' % self._module_ns)
        instance_id = self.ref('%s.sta_instance_04' % self._module_ns)

        data = dict(assembly_category_id=assembly_category_id,
                    instance_id=instance_id,
                    months_before_end_of_mandate=12)

        self.assertRaises(orm.except_orm, self.registry('sta.assembly').create, self.cr, self.uid, data)
