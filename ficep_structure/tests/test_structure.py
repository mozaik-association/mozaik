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

from openerp.addons.ficep_base.tests.test_abstract_ficep import abstract_ficep


_logger = logging.getLogger(__name__)


class test_sta_structure(abstract_ficep, SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        'data/structure_data.xml',
    )

    _module_ns = 'ficep_structure'

    def setUp(self):
        super(test_sta_structure, self).setUp()

        self.model_abstract = self.registry('sta.power.level')
        self.invalidate_success_ids = [
                            self.ref('%s.sta_power_level_10' % self._module_ns)
                                      ]
        self.invalidate_fail_ids = [
                            self.ref('%s.sta_power_level_01' % self._module_ns)
                                   ]
        self.validate_ids = [
                            self.ref('%s.sta_power_level_10' % self._module_ns)
                            ]

    def test_sta_assembly_consistence(self):
        '''
        Cannot create an assembly with a category and an instance of
        different power level
        '''
        assembly_category_id = \
                    self.ref('%s.sta_assembly_category_06' % self._module_ns)
        instance_id = self.ref('%s.sta_instance_04' % self._module_ns)

        data = dict(
            assembly_category_id=assembly_category_id,
            instance_id=instance_id,
        )

        self.assertRaises(orm.except_orm,
                          self.registry('sta.assembly').create,
                          self.cr,
                          self.uid,
                          data)

    def test_create_ext_assembly(self):
        '''
        Allow to create an external assembly without any constraint
        '''
        cr, uid, context = self.cr, self.uid, {}
        ext_assembly_model = self.registry('ext.assembly')
        assembly_category_id = \
                self.ref('%s.ext_assembly_category_01' % self._module_ns)
        instance_id = self.ref('%s.int_instance_01' % self._module_ns)
        fgtb_id = self.ref('%s.res_partner_fgtb' % self._module_ns)

        data = dict(
            assembly_category_id=assembly_category_id,
            instance_id=instance_id,
            ref_partner_id=fgtb_id,
        )

        # Create the assembly
        ext_id = ext_assembly_model.create(cr, uid, data, context=context)

        # Check for is_assembly flag on related created partner
        assembly = ext_assembly_model.browse(cr, uid, ext_id, context=context)
        self.assertTrue(assembly.partner_id.is_assembly,
                       'Create external assembly fails with wrong is_assembly')
