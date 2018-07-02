# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_structure, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_structure is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_structure is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_structure.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.osv import orm

from openerp.addons.mozaik_base.tests.test_abstract_model import \
    test_abstract_model


_logger = logging.getLogger(__name__)


class test_sta_structure(test_abstract_model, SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        'data/structure_data.xml',
    )

    _module_ns = 'mozaik_structure'

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
        self.assertTrue(
            assembly.partner_id.is_assembly,
            'Create external assembly fails with wrong is_assembly')

    def test_get_followers_assemblies(self):
        cr, uid, context = self.cr, self.uid, {}
        instance_obj = self.registry['int.instance']
        power_level_obj = self.registry['int.power.level']
        assembly_obj = self.registry['int.assembly']
        categ_obj = self.registry['int.assembly.category']

        vals = {
            'name': 'Mega Power',
            'sequence': 1,
        }
        power_level_id = power_level_obj.create(
            cr, uid, vals, context=context)
        vals = {
            'name': 'Mega Instance',
            'power_level_id': power_level_id,
        }
        int_instance_id = instance_obj.create(
            cr, uid, vals, context=context)
        vals = {
            'name': 'Mega Assembly',
            'power_level_id': power_level_id,
            'is_secretariat': True,
        }
        categ_id = categ_obj.create(
            cr, uid, vals, context=context)
        vals = {
            'instance_id': int_instance_id,
            'assembly_category_id': categ_id,
            'is_designation_assembly': True,
        }
        assembly_id = assembly_obj.create(
            cr, uid, vals, context=context)
        res_ids = assembly_obj.get_followers_assemblies(
            cr, uid, int_instance_id, context=context)
        self.assertFalse(res_ids, 'Should not have followers result')
        vals = {
            'level_for_followers': True,
        }
        power_level_obj.write(
            cr, uid, power_level_id, vals, context=context)
        res_ids = assembly_obj.get_followers_assemblies(
            cr, uid, int_instance_id, context=context)
        self.assertTrue(len(res_ids) > 0, 'Should have followers result')
        partner_id = assembly_obj.read(
            cr, uid, assembly_id, ['partner_id'],
            context=context)['partner_id'][0]
        self.assertTrue(partner_id in res_ids, 'Should contains this partner '
                        'into the follower result')
