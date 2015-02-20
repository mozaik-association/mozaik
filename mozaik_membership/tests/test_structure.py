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


_logger = logging.getLogger(__name__)


class test_structure(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml'
    )

    _module_ns = 'mozaik_membership'

    def setUp(self):
        super(test_structure, self).setUp()

        self.model_abstract = self.registry('sta.power.level')

        self.sta_assembly_model = self.registry('sta.assembly')
        self.ext_assembly_model = self.registry('ext.assembly')

        self.sta_assembly_category_id = self.ref('%s.sta_assembly_category_14'
                                                 % self._module_ns)
        self.ext_assembly_category_id = self.ref('%s.ext_assembly_category_01'
                                                 % self._module_ns)

    def test_internal_inst_of_assembly_partner(self):
        '''
        When creating or updating an assembly the responsible Internal
        Instance of the result Partner must be automatically set
        '''
        cr, uid, context = self.cr, self.uid, {}
        sta_assembly_model = self.sta_assembly_model
        ext_assembly_model = self.ext_assembly_model

        sta_assembly_category_id, ext_assembly_category_id = \
            self.sta_assembly_category_id, self.ext_assembly_category_id

        # 1/ For an external Assembly
        instance_id = self.ref('%s.int_instance_04' % self._module_ns)
        fgtb_id = self.ref('%s.res_partner_fgtb' % self._module_ns)

        # 1.1/ Create the assembly
        data = dict(
            assembly_category_id=ext_assembly_category_id,
            instance_id=instance_id,
            ref_partner_id=fgtb_id,
        )

        ext_id = ext_assembly_model.create(cr, uid, data, context=context)

        # Check for int_instance_id on related created partner
        assembly = ext_assembly_model.browse(cr, uid, ext_id, context=context)
        self.assertEqual(assembly.partner_id.int_instance_id.id, instance_id,
                         'Create external assembly fails with wrong internal \
                         instance linked to the result partner')

        # 1.2/ Update the assembly
        instance_id = self.ref('%s.int_instance_09' % self._module_ns)
        data = dict(
            instance_id=instance_id,
        )

        ext_assembly_model.write(cr, uid, ext_id, data, context=context)

        # Check for int_instance_id on related partner
        assembly = ext_assembly_model.browse(cr, uid, ext_id, context=context)
        self.assertEqual(assembly.partner_id.int_instance_id.id, instance_id,
                         'Update external assembly fails with wrong internal \
                         instance linked to the result partner')

        # 2/ For a State Assembly
        instance_id = self.ref('%s.sta_instance_07' % self._module_ns)

        # 2.1/ Create the assembly
        data = dict(
            assembly_category_id=sta_assembly_category_id,
            instance_id=instance_id,
        )

        sta_id = sta_assembly_model.create(cr, uid, data, context=context)

        # Check for is_assembly flag on related created partner
        assembly = sta_assembly_model.browse(cr, uid, sta_id, context=context)
        self.assertEqual(assembly.partner_id.int_instance_id.id,
                         assembly.instance_id.int_instance_id.id,
                         'Create state assembly fails with wrong internal \
                         instance linked to the result partner')

        # 2.2/ Update the assembly
        instance_id = self.ref('%s.sta_instance_09' % self._module_ns)
        data = dict(
            instance_id=instance_id,
        )

        sta_assembly_model.write(cr, uid, sta_id, data, context=context)

        # Check for int_instance_id on related partner
        assembly = sta_assembly_model.browse(cr, uid, sta_id, context=context)
        self.assertEqual(assembly.partner_id.int_instance_id.id,
                         assembly.instance_id.int_instance_id.id,
                         'Update state assembly fails with wrong internal \
                         instance linked to the result partner')
