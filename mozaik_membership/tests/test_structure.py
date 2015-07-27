# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from anybox.testing.openerp import SharedSetupTransactionCase


_logger = logging.getLogger(__name__)


class test_structure(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_base/tests/data/res_users_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        'data/res_partner_data.xml',
    )

    _module_ns = 'mozaik_membership'

    def setUp(self):
        super(test_structure, self).setUp()

        self.model_users = self.registry('res.users')
        self.model_int_instance = self.registry('int.instance')
        self.model_power_level = self.registry('int.power.level')

        self.sta_assembly_model = self.registry('sta.assembly')
        self.ext_assembly_model = self.registry('ext.assembly')

        self.sta_assembly_category_id = self.ref('%s.sta_assembly_category_14'
                                                 % self._module_ns)
        self.ext_assembly_category_id = self.ref('%s.ext_assembly_category_01'
                                                 % self._module_ns)
        self.marc_id = self.ref('%s.res_users_marc' % self._module_ns)
        self.conf_id = self.ref('mozaik_base.mozaik_res_groups_configurator')

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

    def test_create_internal_instance(self):
        '''
        When creating an internal root instance
        the new instance has to be added to user's Internal Instances if it
        is not the superuser
        '''
        cr, uid, context = self.cr, self.uid, {}
        uuid = self.marc_id
        res_users_model = self.model_users
        model_int_instance = self.model_int_instance
        model_power_level = self.model_power_level

        # 1/ Update User: make it a configurator
        marc = res_users_model.browse(cr, uid, uuid, context=context)
        marc.update({'groups_id': [(4, self.conf_id)]})

        # 1.1/ Verify test data
        initial_iis = set(marc.partner_id.int_instance_m2m_ids.ids)
        default_inst_id = model_int_instance.get_default(
            cr, uid, context=context)
        self.assertEqual(initial_iis, set([default_inst_id]),
                         'Verifying test data fails '
                         'with wrong internal instances linked '
                         'to the user''s partner')

        # 2/ Create an instance with a parent_id
        default_power_id = model_power_level.get_default(
            cr, uid, context=context)
        vals = {
            'name': 'Test-ins-1',
            'power_level_id': default_power_id,
            'parent_id': default_inst_id,
        }
        ctx = res_users_model.context_get(cr, uuid)
        ctx.update(mail_create_nolog=True)
        model_int_instance.create(cr, uuid, vals, context=ctx)
        # users's internal instances must remain unchanged
        new_iis = set(marc.partner_id.int_instance_m2m_ids.ids) - initial_iis
        self.assertFalse(new_iis,
                         'Create an internal instance with a parent fails '
                         'with wrong internal instances linked '
                         'to the user''s partner')

        # 3/ Create a root instance
        vals.pop('parent_id')
        vals['name'] = 'Test-ins-2'
        newi = model_int_instance.create(cr, uuid, vals, context=ctx)
        # users's internal instances must be completed with the new one
        new_iis = set(marc.partner_id.int_instance_m2m_ids.ids) - initial_iis
        self.assertEqual(new_iis, set([newi]),
                         'Create a root internal instance fails '
                         'with wrong internal instances linked '
                         'to the user''s partner')
