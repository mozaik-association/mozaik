# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import SavepointCase

from datetime import date
from dateutil.relativedelta import relativedelta


class TestCopyMandateWizard(SavepointCase):

    _module_ns = 'mozaik_mandate'

    def test_renew_legislative_state_mandate(self):
        '''
        Try to renew a legislative state mandate which is not allowed
        '''
        stam_thierry_communal_2012 =\
            self.env.ref('%s.stam_thierry_communal_2012' % self._module_ns)

        context = {
            'active_ids': [stam_thierry_communal_2012.id],
            'active_model': 'sta.mandate',
        }
        stam_thierry_communal_2012.sta_assembly_id.assembly_category_id\
            .is_legislative = True
        wizard_object = self.env['copy.sta.mandate.wizard']
        wizard = wizard_object.with_context(context).create({})
        self.assertEqual(wizard.action, 'renew')
        self.assertNotEqual(wizard.message, False, wizard.message)

    def test_renew_non_legislative_state_mandate(self):
        '''
        Renew a non-legislative state mandate
        '''
        stam_thierry_bourgmestre_2012_id =\
            self.ref('%s.stam_thierry_bourgmestre_2012' % self._module_ns)
        legislature_01_id = self.ref('%s.legislature_01' % self._module_ns)
        mandate_object = self.env['sta.mandate']

        context = {
            'active_ids': [stam_thierry_bourgmestre_2012_id],
            'active_model': 'sta.mandate',
        }
        wizard_object = self.env['copy.sta.mandate.wizard']
        wizard = wizard_object.with_context(context).create({})
        self.assertEqual(wizard.action, 'renew')
        self.assertEqual(wizard.message, False)
        self.assertEqual(wizard.legislature_id.id, legislature_01_id)
        wizard.onchange_legislature_id()
        res = wizard.renew_mandate()
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = mandate_object.browse(stam_thierry_bourgmestre_2012_id)
        new_mandate = mandate_object.browse(new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertEqual(base_mandate.mandate_category_id,
                         new_mandate.mandate_category_id)
        self.assertNotEqual(base_mandate.legislature_id,
                            new_mandate.legislature_id)
        self.assertEqual(base_mandate.sta_assembly_id,
                         new_mandate.sta_assembly_id)
        self.assertEqual(base_mandate.with_revenue_declaration,
                         new_mandate.with_revenue_declaration)
        self.assertEqual(base_mandate.with_assets_declaration,
                         new_mandate.with_assets_declaration)

    def test_renew_internal_mandate(self):
        '''
        Try to renew an internal mandate
        '''
        mandate_object = self.env['int.mandate']
        base_mandate = self.browse_ref(
            '%s.intm_thierry_secretaire_done' % self._module_ns)

        context = {
            'active_ids': [base_mandate.id],
            'active_model': 'int.mandate',
        }
        wizard_object = self.env['copy.int.mandate.wizard']
        wizard = wizard_object.with_context(context).create({})
        self.assertEqual(wizard.action, 'renew')
        self.assertEqual(wizard.message, False)

        new_start = fields.Date.to_string(fields.Date.from_string(
            base_mandate.end_date) + relativedelta(days=1))
        new_deadline = fields.Date.to_string(
            date.today() + relativedelta(years=1))
        values = {'start_date': new_start, 'deadline_date': new_deadline}

        wizard.write(values)
        res = wizard.renew_mandate()
        new_mandate_id = res['res_id']
        self.assertTrue(new_mandate_id)

        new_mandate = mandate_object.browse(new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertEqual(base_mandate.mandate_category_id,
                         new_mandate.mandate_category_id)
        self.assertEqual(base_mandate.int_assembly_id,
                         new_mandate.int_assembly_id)
        self.assertEqual(new_start, new_mandate.start_date)
        self.assertEqual(new_deadline, new_mandate.deadline_date)
        self.assertFalse(new_mandate.end_date)

    def test_create_complementary_internal_mandate(self):
        '''
        Create complementary mandate from an existing
        '''
        mandate_object = self.env['int.mandate']
        stam_paul_regional = self.env.ref('%s.intm_paul_regional' %
                                          self._module_ns)
        mc_secretaire_regional_id = self.ref('%s.mc_secretaire_regional' %
                                             self._module_ns)
        assembly_id = self.ref('mozaik_structure.int_assembly_01')

        context = {
            'active_ids': [stam_paul_regional.id],
            'active_model': 'int.mandate',
        }

        wizard_object = self.env['copy.int.mandate.wizard']
        wizard = wizard_object.with_context(context).create({})
        self.assertEqual(wizard.action, 'add')
        self.assertEqual(wizard.message, False)

        values = dict(start_date='2014-12-01',
                      deadline_date='2018-04-15',
                      new_mandate_category_id=mc_secretaire_regional_id,
                      new_assembly_id=assembly_id)
        wizard.write(values)

        res = wizard.add_mandate()
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = stam_paul_regional
        new_mandate = mandate_object.browse(new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertNotEqual(base_mandate.mandate_category_id,
                            new_mandate.mandate_category_id)
        self.assertNotEqual(base_mandate.int_assembly_id,
                            new_mandate.int_assembly_id)
        self.assertEqual(base_mandate.with_revenue_declaration,
                         new_mandate.with_revenue_declaration)
        self.assertEqual(base_mandate.with_assets_declaration,
                         new_mandate.with_assets_declaration)

    def test_renew_external_mandate(self):
        '''
        Try to renew an external mandate
        '''
        mandate_object = self.env['ext.mandate']
        extm_thierry_membre_ag = self.env.ref(
            '%s.extm_thierry_membre_ag_done' % self._module_ns)

        context = {
            'active_ids': [extm_thierry_membre_ag.id],
            'active_model': 'ext.mandate',
        }
        wizard_object = self.env['copy.ext.mandate.wizard']
        wizard = wizard_object.with_context(context).create({})
        self.assertEqual(wizard.action, 'renew')
        self.assertEqual(wizard.message, False)

        values = dict(start_date='2014-12-03',
                      deadline_date='2020-12-03')

        wizard.write(values)
        res = wizard.renew_mandate()
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = extm_thierry_membre_ag
        new_mandate = mandate_object.browse(new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertEqual(base_mandate.mandate_category_id,
                         new_mandate.mandate_category_id)
        self.assertEqual(base_mandate.ext_assembly_id,
                         new_mandate.ext_assembly_id)
        self.assertEqual(base_mandate.with_revenue_declaration,
                         new_mandate.with_revenue_declaration)
        self.assertEqual(base_mandate.with_assets_declaration,
                         new_mandate.with_assets_declaration)

    def test_create_complementary_external_mandate(self):
        '''
        Create complementary mandate from an existing
        '''
        mandate_object = self.env['ext.mandate']
        extm_paul_membre_ag = self.env.ref('%s.extm_paul_membre_ag' %
                                           self._module_ns)
        mc_admin_id = self.ref('%s.mc_administrateur' % self._module_ns)
        assembly_id = self.env.ref('mozaik_structure.ext_assembly_01')

        context = {
            'active_ids': [extm_paul_membre_ag.id],
            'active_model': 'ext.mandate',
        }

        wizard_object = self.env['copy.ext.mandate.wizard']
        wizard = wizard_object.with_context(context).create({})
        self.assertEqual(wizard.action, 'add')
        self.assertEqual(wizard.message, False)

        ac = assembly_id.assembly_category_id.copy({"name": "test"})

        values = dict(start_date='2014-12-01',
                      deadline_date='2018-04-15',
                      new_mandate_category_id=mc_admin_id,
                      new_assembly_id=assembly_id.copy(
                          {"assembly_category_id": ac.id}).id)
        wizard.write(values)

        res = wizard.add_mandate()
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        new_mandate = mandate_object.browse(new_mandate_id)

        self.assertEqual(extm_paul_membre_ag.partner_id,
                         new_mandate.partner_id)
        self.assertNotEqual(extm_paul_membre_ag.mandate_category_id,
                            new_mandate.mandate_category_id)
        self.assertNotEqual(extm_paul_membre_ag.ext_assembly_id,
                            new_mandate.ext_assembly_id)
        self.assertEqual(extm_paul_membre_ag.with_revenue_declaration,
                         new_mandate.with_revenue_declaration)
        self.assertEqual(extm_paul_membre_ag.with_assets_declaration,
                         new_mandate.with_assets_declaration)
