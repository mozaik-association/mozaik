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

import psycopg2
import logging
from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.addons.mozaik_base import testtool

_logger = logging.getLogger(__name__)


class test_mandate(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'mozaik_mandate'

    def setUp(self):
        super(test_mandate, self).setUp()

    def test_avoid_duplicate_mandate_category(self):
        '''
            Test unique name of mandate category
        '''
        data = dict(name='category_01')
        self.registry('mandate.category').create(self.cr, self.uid, data)

        with testtool.disable_log_error(self.cr):
            self.assertRaises(psycopg2.IntegrityError,
                              self.registry('mandate.category').create,
                              self.cr, self.uid, data)

    def test_exclusive_mandate_category_consistency(self):
        '''
            Test consistency between exclusive mandate categories
        '''
        sta_assembly_id = self.ref('%s.sta_assembly_category_01' %
                                   self._module_ns)
        ext_assembly_id = self.ref('%s.ext_assembly_category_01' %
                                   self._module_ns)

        category_pool = self.registry('mandate.category')

        test_category_id_1 =\
                    category_pool.create(
                                  self.cr,
                                  self.uid,
                                  dict(
                                   name='Category 1',
                                   type='sta',
                                   sta_assembly_category_id=sta_assembly_id))
        '''
            Test consistency on create
        '''
        magic_number = [[6, False, [test_category_id_1]]]
        test_category_id_2 =\
                    category_pool.create(
                                  self.cr,
                                  self.uid,
                                  dict(
                                   name='Category 2',
                                   type='ext',
                                   ext_assembly_category_id=ext_assembly_id,
                                   exclusive_category_m2m_ids=magic_number))

        exclu_ids = category_pool.read(self.cr,
                                       self.uid,
                                       test_category_id_1,
                                       ['exclusive_category_m2m_ids']
                                       )['exclusive_category_m2m_ids']
        self.assertTrue(test_category_id_2 in exclu_ids)

        '''
            Remove exclusive relation to test write method
        '''
        category_pool.write(self.cr,
                            self.uid,
                            test_category_id_2,
                            dict(exclusive_category_m2m_ids=[[6, False, []]]))
        exclu_ids = category_pool.read(self.cr,
                                       self.uid,
                                       test_category_id_1,
                                       ['exclusive_category_m2m_ids']
                                       )['exclusive_category_m2m_ids']
        self.assertFalse(exclu_ids)

        '''
            Add again exclusive relation to test write method
        '''
        magic_number = [[6, False, [test_category_id_1]]]
        category_pool.write(self.cr,
                            self.uid,
                            test_category_id_2,
                            dict(exclusive_category_m2m_ids=magic_number))
        exclu_ids = category_pool.read(self.cr,
                                       self.uid,
                                       test_category_id_1,
                                       ['exclusive_category_m2m_ids']
                                       )['exclusive_category_m2m_ids']
        self.assertTrue(test_category_id_2 in exclu_ids)

    def test_exclusive_mandates(self):
        '''
            Test detection of exclusive mandates
        '''
        mc_bourgmestre_id = self.ref('%s.mc_bourgmestre' % self._module_ns)
        mc_membre_effectif_ag_id = self.ref('%s.mc_membre_effectif_ag' %
                                            self._module_ns)
        jacques_partner_id = self.ref('%s.res_partner_jacques' %
                                      self._module_ns)

        sta_mandate_pool = self.registry('sta.mandate')
        ext_mandate_pool = self.registry('ext.mandate')
        '''
            Categories are exclusives
        '''
        self.registry('mandate.category').write(self.cr,
                                                self.uid,
                                                mc_bourgmestre_id,
                                                {'exclusive_category_m2m_ids':
                                                [[6,
                                                  False,
                                                  [mc_membre_effectif_ag_id]]]
                                                 })
        '''
            Create a mandate in first category
        '''
        data = dict(mandate_category_id=mc_bourgmestre_id,
                    designation_int_assembly_id=self.ref('%s.int_assembly_01' %
                                                         self._module_ns),
                    legislature_id=self.ref('%s.legislature_01' %
                                            self._module_ns),
                    start_date="2022-12-03",
                    deadline_date="2024-04-15",
                    sta_assembly_id=self.ref('%s.sta_assembly_01' %
                                             self._module_ns),
                    partner_id=jacques_partner_id)

        mandate_id_1 = sta_mandate_pool.create(self.cr, self.uid, data)

        '''
            Create a mandate in first category
        '''
        data = dict(mandate_category_id=mc_membre_effectif_ag_id,
                    designation_int_assembly_id=self.ref('%s.int_assembly_01' %
                                                         self._module_ns),
                    start_date="2022-12-03",
                    deadline_date="2024-04-15",
                    ext_assembly_id=self.ref('%s.ext_assembly_02' %
                                             self._module_ns),
                    partner_id=jacques_partner_id)

        mandate_id_2 = ext_mandate_pool.create(self.cr, self.uid, data)

        '''
            System should have detected mandates as exclusive
        '''
        mandata_data_1 = sta_mandate_pool.read(self.cr,
                                               self.uid,
                                               mandate_id_1,
                                               ['is_duplicate_detected',
                                                'is_duplicate_allowed'])
        self.assertTrue(mandata_data_1['is_duplicate_detected'])
        self.assertFalse(mandata_data_1['is_duplicate_allowed'])

        mandata_data_2 = ext_mandate_pool.read(self.cr,
                                               self.uid, mandate_id_2,
                                               ['is_duplicate_detected',
                                                'is_duplicate_allowed'])
        self.assertTrue(mandata_data_2['is_duplicate_detected'])
        self.assertFalse(mandata_data_2['is_duplicate_allowed'])

        '''
            Allow exclusive mandates
        '''
        ids = self.registry('generic.mandate').search(
                                                  self.cr,
                                                  self.uid,
                                                  [('mandate_id', 'in',
                                                  [mandate_id_1, mandate_id_2])
                                                  ])

        ctx = {'active_model': 'generic.mandate',
               'active_ids': ids,
               'multi_model': True,
               'model_id_name': 'mandate_id'}

        wz_id = self.registry('allow.duplicate.wizard').create(self.cr,
                                                               self.uid,
                                                               {},
                                                               context=ctx)
        self.registry('allow.duplicate.wizard').button_allow_duplicate(
                                                        self.cr,
                                                        self.uid,
                                                        wz_id,
                                                        context=ctx)

        mandata_data_1 = sta_mandate_pool.read(self.cr,
                                               self.uid,
                                               mandate_id_1,
                                               ['is_duplicate_detected',
                                                'is_duplicate_allowed'])
        self.assertFalse(mandata_data_1['is_duplicate_detected'])
        self.assertTrue(mandata_data_1['is_duplicate_allowed'])

        mandata_data_2 = ext_mandate_pool.read(self.cr,
                                               self.uid,
                                               mandate_id_2,
                                               ['is_duplicate_detected',
                                                'is_duplicate_allowed'])
        self.assertFalse(mandata_data_2['is_duplicate_detected'])
        self.assertTrue(mandata_data_2['is_duplicate_allowed'])

        '''
            Undo allow exclusive mandates
        '''
        sta_mandate_pool.button_undo_allow_duplicate(self.cr,
                                                     self.uid,
                                                     [mandate_id_1])
        mandata_data_1 = sta_mandate_pool.read(self.cr,
                                               self.uid,
                                               mandate_id_1,
                                               ['is_duplicate_detected',
                                                'is_duplicate_allowed'])
        self.assertTrue(mandata_data_1['is_duplicate_detected'])
        self.assertFalse(mandata_data_1['is_duplicate_allowed'])

        mandata_data_2 = ext_mandate_pool.read(self.cr,
                                               self.uid,
                                               mandate_id_2,
                                               ['is_duplicate_detected',
                                                'is_duplicate_allowed'])
        self.assertTrue(mandata_data_2['is_duplicate_detected'])
        self.assertFalse(mandata_data_2['is_duplicate_allowed'])
