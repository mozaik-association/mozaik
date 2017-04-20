# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from anybox.testing.openerp import SharedSetupTransactionCase

_logger = logging.getLogger(__name__)


class test_copy_mandate_wizard(SharedSetupTransactionCase):
    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'mozaik_mandate'

    def setUp(self):
        super(test_copy_mandate_wizard, self).setUp()
        cr, uid = self.cr, self.uid

        sta_candidature_pool = self.registry('sta.candidature')
        sta_committee_pool = self.registry('sta.selection.committee')
        sta_paul_communal_id = self.ref('%s.sta_paul_communal' %
                                        self._module_ns)
        sta_pauline_communal_id = self.ref('%s.sta_pauline_communal' %
                                           self._module_ns)
        sta_marc_communal_id = self.ref('%s.sta_marc_communal' %
                                        self._module_ns)
        sta_thierry_communal_id = self.ref('%s.sta_thierry_communal' %
                                           self._module_ns)
        sta_jacques_communal_id = self.ref('%s.sta_jacques_communal' %
                                           self._module_ns)
        selection_committee_id = self.ref('%s.sc_tete_huy_communale' %
                                          self._module_ns)

        accepted_ids = [sta_thierry_communal_id]
        rejected_ids = [sta_pauline_communal_id,
                        sta_marc_communal_id,
                        sta_paul_communal_id,
                        sta_jacques_communal_id]

        sta_candidature_pool.signal_workflow(cr,
                                             uid,
                                             accepted_ids,
                                             'button_suggest',
                                             context={})
        sta_candidature_pool.signal_workflow(cr,
                                             uid,
                                             rejected_ids,
                                             'button_reject',
                                             context={})
        sta_committee_pool.button_accept_candidatures(cr,
                                                      uid,
                                                      [selection_committee_id])
        sta_candidature_pool.signal_workflow(cr,
                                             uid,
                                             accepted_ids,
                                             'button_elected', context={})
        sta_candidature_pool.button_create_mandate(self.cr,
                                                   self.uid,
                                                   accepted_ids)

    def test_renew_legislative_state_mandate(self):
        '''
        Try to renew a legislative state mandate which is not allowed
        '''
        stam_thierry_communal_2012_id =\
            self.ref('%s.stam_thierry_communal_2012' % self._module_ns)

        context = {
            'active_ids': [stam_thierry_communal_2012_id],
            'active_model': 'sta.mandate',
        }
        wizard_pool = self.registry('copy.sta.mandate.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {}, context=context)
        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)
        self.assertEqual(wizard.action, 'renew')
        self.assertNotEqual(wizard.message, False, wizard.message)

    def test_renew_non_legislative_state_mandate(self):
        '''
        Renew a non-legislative state mandate
        '''
        stam_thierry_bourgmestre_2012_id =\
            self.ref('%s.stam_thierry_bourgmestre_2012' % self._module_ns)
        legislature_01_id = self.ref('%s.legislature_01' % self._module_ns)
        mandate_pool = self.registry('sta.mandate')

        context = {
            'active_ids': [stam_thierry_bourgmestre_2012_id],
            'active_model': 'sta.mandate',
        }
        wizard_pool = self.registry('copy.sta.mandate.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {}, context=context)
        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)
        self.assertEqual(wizard.action, 'renew')
        self.assertEqual(wizard.message, False)
        self.assertEqual(wizard.legislature_id.id, legislature_01_id)
        data = wizard_pool.onchange_legislature_id(self.cr,
                                                   self.uid,
                                                   [wiz_id],
                                                   wizard.legislature_id.id,
                                                   context=context)
        values = dict(start_date=data['value']['start_date'],
                      deadline_date=data['value']['deadline_date'])
        wizard_pool.write(self.cr, self.uid, wiz_id, values)
        res = wizard_pool.renew_mandate(self.cr, self.uid, [wiz_id],
                                        context=context)
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = mandate_pool.browse(self.cr, self.uid,
                                           stam_thierry_bourgmestre_2012_id)
        new_mandate = mandate_pool.browse(self.cr, self.uid,
                                          new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertEqual(base_mandate.mandate_category_id,
                         new_mandate.mandate_category_id)
        self.assertNotEqual(base_mandate.legislature_id,
                            new_mandate.legislature_id)
        self.assertEqual(base_mandate.sta_assembly_id,
                         new_mandate.sta_assembly_id)
        self.assertEqual(base_mandate.is_submission_mandate,
                         new_mandate.is_submission_mandate)
        self.assertEqual(base_mandate.is_submission_assets,
                         new_mandate.is_submission_assets)

    def test_create_complementary_state_mandate(self):
        '''
        Create complementary mandate from an existing
        '''
        mandate_pool = self.registry('sta.mandate')
        sta_thierry_communal_id = self.ref('%s.sta_thierry_communal' %
                                           self._module_ns)
        mc_bourgmestre_id = self.ref('%s.mc_bourgmestre' % self._module_ns)
        college_assembly_id = self.ref('%s.sta_assembly_03' % self._module_ns)
        mandate_id = mandate_pool.search(self.cr, self.uid,
                                         [('candidature_id',
                                           '=', sta_thierry_communal_id)
                                          ])[0]

        context = {
            'active_ids': [mandate_id],
            'active_model': 'sta.mandate',
        }

        wizard_pool = self.registry('copy.sta.mandate.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {}, context=context)
        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)
        self.assertEqual(wizard.action, 'add')
        self.assertEqual(wizard.message, False)

        data = wizard_pool.onchange_legislature_id(self.cr, self.uid, [wiz_id],
                                                   wizard.legislature_id.id,
                                                   context=context)
        values = dict(start_date=data['value']['start_date'],
                      deadline_date=data['value']['deadline_date'],
                      new_mandate_category_id=mc_bourgmestre_id,
                      new_assembly_id=college_assembly_id)
        wizard_pool.write(self.cr, self.uid, wiz_id, values)

        res = wizard_pool.add_mandate(self.cr, self.uid, [wiz_id],
                                      context=context)
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = mandate_pool.browse(self.cr, self.uid, mandate_id)
        new_mandate = mandate_pool.browse(self.cr, self.uid, new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertNotEqual(base_mandate.mandate_category_id,
                            new_mandate.mandate_category_id)
        self.assertEqual(base_mandate.legislature_id,
                         new_mandate.legislature_id)
        self.assertNotEqual(base_mandate.sta_assembly_id,
                            new_mandate.sta_assembly_id)
        self.assertEqual(base_mandate.is_submission_mandate,
                         new_mandate.is_submission_mandate)
        self.assertEqual(base_mandate.is_submission_assets,
                         new_mandate.is_submission_assets)

    def test_renew_internal_mandate(self):
        '''
        Try to renew an internal mandate
        '''
        mandate_pool = self.registry('int.mandate')
        stam_thierry_secretaire_id = self.ref(
            '%s.intm_thierry_secretaire_done' % self._module_ns)

        context = {
            'active_ids': [stam_thierry_secretaire_id],
            'active_model': 'int.mandate',
        }
        wizard_pool = self.registry('copy.int.mandate.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {}, context=context)
        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)
        self.assertEqual(wizard.action, 'renew')
        self.assertEqual(wizard.message, False)

        values = dict(start_date='2014-12-03',
                      deadline_date='2020-12-03')

        wizard_pool.write(self.cr, self.uid, wiz_id, values)
        res = wizard_pool.renew_mandate(self.cr, self.uid, [wiz_id],
                                        context=context)
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = mandate_pool.browse(self.cr, self.uid,
                                           stam_thierry_secretaire_id)
        new_mandate = mandate_pool.browse(self.cr, self.uid, new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertEqual(base_mandate.mandate_category_id,
                         new_mandate.mandate_category_id)
        self.assertEqual(base_mandate.int_assembly_id,
                         new_mandate.int_assembly_id)
        self.assertEqual(base_mandate.is_submission_mandate,
                         new_mandate.is_submission_mandate)
        self.assertEqual(base_mandate.is_submission_assets,
                         new_mandate.is_submission_assets)

    def test_create_complementary_internal_mandate(self):
        '''
        Create complementary mandate from an existing
        '''
        mandate_pool = self.registry('int.mandate')
        stam_paul_regional_id = self.ref('%s.intm_paul_regional' %
                                         self._module_ns)
        mc_secretaire_regional_id = self.ref('%s.mc_secretaire_regional' %
                                             self._module_ns)
        assembly_id = self.ref('%s.int_assembly_03' % self._module_ns)

        context = {
            'active_ids': [stam_paul_regional_id],
            'active_model': 'int.mandate',
        }

        wizard_pool = self.registry('copy.int.mandate.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {}, context=context)
        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)
        self.assertEqual(wizard.action, 'add')
        self.assertEqual(wizard.message, False)

        values = dict(start_date='2014-12-01',
                      deadline_date='2018-04-15',
                      new_mandate_category_id=mc_secretaire_regional_id,
                      new_assembly_id=assembly_id)
        wizard_pool.write(self.cr, self.uid, wiz_id, values)

        res = wizard_pool.add_mandate(self.cr, self.uid, [wiz_id],
                                      context=context)
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = mandate_pool.browse(self.cr, self.uid,
                                           stam_paul_regional_id)
        new_mandate = mandate_pool.browse(self.cr, self.uid,
                                          new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertNotEqual(base_mandate.mandate_category_id,
                            new_mandate.mandate_category_id)
        self.assertNotEqual(base_mandate.int_assembly_id,
                            new_mandate.int_assembly_id)
        self.assertEqual(base_mandate.is_submission_mandate,
                         new_mandate.is_submission_mandate)
        self.assertEqual(base_mandate.is_submission_assets,
                         new_mandate.is_submission_assets)

    def test_renew_external_mandate(self):
        '''
        Try to renew an external mandate
        '''
        mandate_pool = self.registry('ext.mandate')
        extm_thierry_membre_ag_id = self.ref(
            '%s.extm_thierry_membre_ag_done' % self._module_ns)

        context = {
            'active_ids': [extm_thierry_membre_ag_id],
            'active_model': 'ext.mandate',
        }
        wizard_pool = self.registry('copy.ext.mandate.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {}, context=context)
        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)
        self.assertEqual(wizard.action, 'renew')
        self.assertEqual(wizard.message, False)

        values = dict(start_date='2014-12-03',
                      deadline_date='2020-12-03')

        wizard_pool.write(self.cr, self.uid, wiz_id, values)
        res = wizard_pool.renew_mandate(self.cr, self.uid, [wiz_id],
                                        context=context)
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = mandate_pool.browse(self.cr, self.uid,
                                           extm_thierry_membre_ag_id)
        new_mandate = mandate_pool.browse(self.cr, self.uid, new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertEqual(base_mandate.mandate_category_id,
                         new_mandate.mandate_category_id)
        self.assertEqual(base_mandate.ext_assembly_id,
                         new_mandate.ext_assembly_id)
        self.assertEqual(base_mandate.is_submission_mandate,
                         new_mandate.is_submission_mandate)
        self.assertEqual(base_mandate.is_submission_assets,
                         new_mandate.is_submission_assets)

    def test_create_complementary_external_mandate(self):
        '''
        Create complementary mandate from an existing
        '''
        mandate_pool = self.registry('ext.mandate')
        extm_paul_membre_ag_id = self.ref('%s.extm_paul_membre_ag' %
                                          self._module_ns)
        mc_admin_id = self.ref('%s.mc_administrateur' % self._module_ns)
        assembly_id = self.ref('%s.ext_assembly_02' % self._module_ns)

        context = {
            'active_ids': [extm_paul_membre_ag_id],
            'active_model': 'ext.mandate',
        }

        wizard_pool = self.registry('copy.ext.mandate.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {}, context=context)
        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)
        self.assertEqual(wizard.action, 'add')
        self.assertEqual(wizard.message, False)

        values = dict(start_date='2014-12-01',
                      deadline_date='2018-04-15',
                      new_mandate_category_id=mc_admin_id,
                      new_assembly_id=assembly_id)
        wizard_pool.write(self.cr, self.uid, wiz_id, values)

        res = wizard_pool.add_mandate(self.cr, self.uid, [wiz_id],
                                      context=context)
        new_mandate_id = res['res_id']
        self.assertNotEqual(new_mandate_id, False)

        base_mandate = mandate_pool.browse(self.cr, self.uid,
                                           extm_paul_membre_ag_id)
        new_mandate = mandate_pool.browse(self.cr, self.uid, new_mandate_id)

        self.assertEqual(base_mandate.partner_id, new_mandate.partner_id)
        self.assertNotEqual(base_mandate.mandate_category_id,
                            new_mandate.mandate_category_id)
        self.assertNotEqual(base_mandate.ext_assembly_id,
                            new_mandate.ext_assembly_id)
        self.assertEqual(base_mandate.is_submission_mandate,
                         new_mandate.is_submission_mandate)
        self.assertEqual(base_mandate.is_submission_assets,
                         new_mandate.is_submission_assets)
