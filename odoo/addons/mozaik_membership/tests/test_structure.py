# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo.tests.common import TransactionCase


_logger = logging.getLogger(__name__)


class TestStructure(TransactionCase):

    def setUp(self):
        super().setUp()

        self.model_users = self.env['res.users']
        self.model_int_instance = self.env['int.instance']
        self.model_power_level = self.env['int.power.level']

        self.sta_assembly_model = self.env['sta.assembly']
        self.ext_assembly_model = self.env['ext.assembly']

        self.sta_assembly_category_id = self.env.ref(
            'mozaik_structure.sta_assembly_category_01')
        self.ext_assembly_category_id = self.env.ref(
            'mozaik_structure.ext_assembly_category_01')
        self.marc_id = self.env.ref('mozaik_membership.res_users_marc')
        self.group_struct = self.env.ref(
            'mozaik_structure.res_groups_structure_manager')

    def test_internal_inst_of_assembly_partner(self):
        '''
        When creating or updating an assembly the responsible Internal
        Instance of the result Partner must be automatically set
        '''
        sta_assembly_model = self.sta_assembly_model
        ext_assembly_model = self.ext_assembly_model

        sta_assembly_category_id, ext_assembly_category_id = \
            self.sta_assembly_category_id, self.ext_assembly_category_id

        # 1/ For an external Assembly
        instance_id = self.env.ref('mozaik_structure.int_instance_02')
        fgtb_id = self.env.ref('mozaik_membership.res_partner_fgtb')

        # 1.1/ Create the assembly
        data = dict(
            assembly_category_id=ext_assembly_category_id.id,
            instance_id=instance_id.id,
            ref_partner_id=fgtb_id.id,
        )

        assembly = ext_assembly_model.create(data)

        # 1.2/ Update the assembly
        instance_id = self.env.ref('mozaik_structure.int_instance_02')
        data = dict(
            instance_id=instance_id.id,
        )

        assembly.write(data)

        # 2/ For a State Assembly
        instance_id = self.env.ref('mozaik_membership.sta_instance_03')

        # 2.1/ Create the assembly
        data = dict(
            assembly_category_id=sta_assembly_category_id.id,
            instance_id=instance_id.id,
        )

        assembly = sta_assembly_model.create(data)

        # Check for is_assembly flag on related created partner
        self.assertTrue(assembly.partner_id.is_assembly)

    def test_create_internal_instance(self):
        '''
        When creating an internal root instance
        the new instance has to be added to user's Internal Instances if it
        is not the superuser
        '''
        marc = self.marc_id
        res_users_model = self.model_users
        model_int_instance = self.model_int_instance
        model_power_level = self.model_power_level

        # 1/ Update User: make it a configurator
        marc.update({'groups_id': [(4, self.group_struct.id)]})

        # 1.1/ Verify test data
        initial_iis = marc.partner_id.int_instance_m2m_ids
        default_inst_id = model_int_instance._get_default_int_instance()
        self.assertEqual(initial_iis, default_inst_id,
                         'Verifying test data fails '
                         'with wrong internal instances linked '
                         'to the user''s partner')

        # 2/ Create an instance with a parent_id
        default_power_id = model_power_level._get_default_int_power_level()
        vals = {
            'name': 'Test-ins-1',
            'power_level_id': default_power_id.id,
            'parent_id': default_inst_id.id,
            'code': '100',
        }
        ctx = res_users_model.context_get()
        ctx.update(tracking_disable=True)
        model_int_instance = model_int_instance.with_context(ctx)
        model_int_instance.create(vals)
        # users's internal instances must remain unchanged
        new_iis = marc.partner_id.int_instance_m2m_ids - initial_iis
        self.assertFalse(new_iis,
                         'Create an internal instance with a parent fails '
                         'with wrong internal instances linked '
                         'to the user''s partner')
