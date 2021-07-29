# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestMandate(SavepointCase):

    def test_avoid_duplicate_mandate_category(self):
        '''
            Test unique name of mandate category
        '''
        data = dict(type='sta', name='category_01')
        self.env['mandate.category'].create(data)
        _logger = logging.getLogger("odoo.sql_db")
        previous_level = _logger.level
        _logger.setLevel(logging.CRITICAL)
        self.assertRaises(ValidationError,
                          self.env['mandate.category'].create,
                          data)
        _logger.setLevel(previous_level)

    def test_exclusive_mandate_category_consistency(self):
        '''
            Test consistency between exclusive mandate categories
        '''
        sta_assembly_id = self.ref('mozaik_structure.sta_assembly_category_01')
        ext_assembly_id = self.ref('mozaik_structure.ext_assembly_category_01')

        category_model = self.env['mandate.category']

        test_category_id_1 =\
            category_model.create(
                dict(
                    name='Category 1',
                    type='sta',
                    sta_assembly_category_id=sta_assembly_id))
        # Test consistency on create
        magic_number = [[6, False, [test_category_id_1.id]]]
        test_category_id_2 =\
            category_model.create(
                dict(
                    name='Category 2',
                    type='ext',
                    ext_assembly_category_id=ext_assembly_id,
                    exclusive_category_m2m_ids=magic_number))

        self.assertTrue(
            test_category_id_2 in
            test_category_id_1.exclusive_category_m2m_ids)

        # Remove exclusive relation to test write method
        test_category_id_2.write(
            dict(exclusive_category_m2m_ids=[[6, False, []]]))
        self.assertFalse(test_category_id_1.exclusive_category_m2m_ids)

        # Add again exclusive relation to test write method
        magic_number = [[6, False, [test_category_id_1.id]]]
        test_category_id_2.write(
            dict(exclusive_category_m2m_ids=magic_number))
        self.assertTrue(
            test_category_id_2 in
            test_category_id_1.exclusive_category_m2m_ids)

    def test_exclusive_mandates(self):
        '''
            Test detection of exclusive mandates
        '''
        mc_bourgmestre = self.env.ref('mozaik_mandate.mc_bourgmestre')
        mc_membre_effectif_ag_id = self.ref(
            'mozaik_mandate.mc_membre_effectif_ag')
        jacques_partner_id = self.ref('mozaik_coordinate.res_partner_jacques')

        sta_mandate_model = self.env['sta.mandate']
        ext_mandate_model = self.env['ext.mandate']
        # Categories are exclusives
        mc_bourgmestre.write(
            {'exclusive_category_m2m_ids':
                [[6, False, [mc_membre_effectif_ag_id]]]
             })
        # Create a mandate in first category
        data = dict(mandate_category_id=mc_bourgmestre.id,
                    designation_int_assembly_id=self.ref(
                        'mozaik_structure.int_assembly_01'),
                    legislature_id=self.ref('mozaik_mandate.legislature_01'),
                    start_date="2022-12-03",
                    deadline_date="2024-04-15",
                    sta_assembly_id=self.ref(
                        'mozaik_structure.sta_assembly_01'),
                    partner_id=jacques_partner_id)

        mandate_id_1 = sta_mandate_model.create(data)

        # Create a mandate in first category
        data = dict(mandate_category_id=mc_membre_effectif_ag_id,
                    designation_int_assembly_id=self.ref(
                        'mozaik_structure.int_assembly_01'),
                    start_date="2022-12-03",
                    deadline_date="2024-04-15",
                    ext_assembly_id=self.ref(
                        'mozaik_structure.ext_assembly_01'),
                    partner_id=jacques_partner_id)

        mandate_id_2 = ext_mandate_model.create(data)

        # System should have detected mandates as exclusive
        self.assertTrue(mandate_id_1.is_duplicate_detected)
        self.assertFalse(mandate_id_1.is_duplicate_allowed)

        self.assertTrue(mandate_id_2.is_duplicate_detected)
        self.assertFalse(mandate_id_2.is_duplicate_allowed)

        # Allow exclusive mandates
        generic_mandate = self.env['generic.mandate'].search(
            [('mandate_id', 'in', [mandate_id_1.id, mandate_id_2.id])])

        ctx = {'active_model': 'generic.mandate',
               'active_ids': generic_mandate.ids,
               'multi_model': True,
               'model_id_name': 'mandate_id'}

        wz_id = self.env['allow.duplicate.wizard'].with_context(ctx).create({})
        wz_id.button_allow_duplicate()

        self.assertFalse(mandate_id_1.is_duplicate_detected)
        self.assertTrue(mandate_id_1.is_duplicate_allowed)

        self.assertFalse(mandate_id_2.is_duplicate_detected)
        self.assertTrue(mandate_id_2.is_duplicate_allowed)

        # Undo allow exclusive mandates
        mandate_id_1.button_undo_allow_duplicate()
        self.assertTrue(mandate_id_1.is_duplicate_detected)
        self.assertFalse(mandate_id_1.is_duplicate_allowed)

        self.assertTrue(mandate_id_2.is_duplicate_detected)
        self.assertFalse(mandate_id_2.is_duplicate_allowed)

    def test_invalidate_mandates(self):
        '''
        Test mandate closing and invalidation
        '''
        m1 = self.env.ref('mozaik_mandate.stam_thierry_communal_2012')
        m2 = self.env.ref('mozaik_mandate.stam_thierry_bourgmestre_2012')
        mandates = m1 | m2
        self.assertFalse(any(mandates.mapped('end_date')))

        mandates.action_invalidate()
        self.assertFalse(any(mandates.mapped('active')))
        self.assertEqual(
            mandates.mapped('end_date'), mandates.mapped('deadline_date'))
