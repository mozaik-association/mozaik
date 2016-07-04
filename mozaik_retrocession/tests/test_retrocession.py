# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_retrocession, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_retrocession is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_retrocession is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_retrocession.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from dateutil.relativedelta import relativedelta
from datetime import datetime
import psycopg2
import logging
from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.osv import fields
from openerp.addons.mozaik_base import testtool

_logger = logging.getLogger(__name__)


class test_retrocession(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        '../../mozaik_mandate/tests/data/mandate_data.xml',
        'data/retrocession_data.xml',
    )

    _module_ns = 'mozaik_retrocession'

    def setUp(self):
        super(test_retrocession, self).setUp()
        self.year = (datetime.today() - relativedelta(years=1)).strftime('%Y')

    def test_fractionation_invalidate(self):
        '''
            Test automatic invalidation of lines of a given fractionation
        '''
        fractionation_pool = self.registry('fractionation')
        fractionation_01 = self.browse_ref('%s.f_sample_02' % self._module_ns)

        fractionation_pool.action_invalidate(
            self.cr, self.uid, [
                fractionation_01.id])

        for line in fractionation_01.fractionation_line_ids:
            self.assertFalse(line.active)

    def test_fractionation_compute_total_percentage(self):
        '''
            Test compute total percentage of all lines
        '''
        fractionation_01 = self.browse_ref('%s.f_sample_01' % self._module_ns)
        self.assertEqual(fractionation_01.total_percentage, 100)

    def test_fractionation_line_percentage(self):
        '''
            Test percentage of line must be lower or equal to 100
        '''
        fractionation_02_id = self.ref('%s.f_sample_02' % self._module_ns)
        int_power_level_02_id = self.ref(
            '%s.int_power_level_02' %
            self._module_ns)
        data = dict(fractionation_id=fractionation_02_id,
                    power_level_id=int_power_level_02_id,
                    percentage=142)

        with testtool.disable_log_error(self.cr):
            self.assertRaises(
                psycopg2.IntegrityError,
                self.registry('fractionation.line').create,
                self.cr,
                self.uid,
                data)

    def test_unicity_fractionation_line(self):
        '''
            Test reference to a power level must unique within a fractionation
        '''
        fractionation_02_id = self.ref('%s.f_sample_02' % self._module_ns)
        int_power_level_01_id = self.ref('mozaik_structure.int_power_level_01')
        data = dict(fractionation_id=fractionation_02_id,
                    power_level_id=int_power_level_01_id,
                    percentage=20)
        with testtool.disable_log_error(self.cr):
            self.assertRaises(psycopg2.IntegrityError,
                              self.registry('fractionation.line').create,
                              self.cr, self.uid, data)

    def test_calculation_method_invalidate(self):
        '''
            Test automatic invalidation of rules of a given calculation method
        '''
        method_pool = self.registry('calculation.method')
        method_01 = self.browse_ref('%s.cm_sample_04' % self._module_ns)

        method_pool.action_invalidate(self.cr, self.uid, [method_01.id])

        for rule in method_01.calculation_rule_ids:
            self.assertFalse(rule.active)

    def test_calculation_method_type(self):
        '''
            Test automatic computation of type
        '''
        rule_pool = self.registry('calculation.rule')
        method_01 = self.browse_ref('%s.cm_sample_01' % self._module_ns)

        data = dict(name="Calculation rule test sample",
                    calculation_method_id=method_01.id,
                    type='variable',
                    percentage=2)

        rule_pool.create(self.cr, self.uid, data)

        self.assertEqual(method_01.type, 'mixed')

    def test_res_partner_invalidate(self):
        '''
            Test automatic invalidation
        '''
        mandate_id = self.ref('%s.extm_paul_membre_ag' % self._module_ns)
        method_id = self.ref('%s.cm_sample_01' % self._module_ns)
        retro_id = self.ref('%s.retro_paul_ag_mai_20xx' % self._module_ns)
        partner_id = self.ref('%s.res_partner_paul' % self._module_ns)
        today = fields.date.today()

        mandate = self.registry('ext.mandate').browse(
            self.cr, self.uid, mandate_id)

        self.registry('res.partner').action_invalidate(
            self.cr, self.uid, [partner_id], context=None)

        self.assertFalse(mandate.active)
        if today < mandate.start_date:
            self.assertEqual(mandate.end_date, mandate.start_date)
        elif today < mandate.deadline_date:
            self.assertEqual(mandate.end_date, today)
        else:
            self.assertLessEqual(mandate.end_date, mandate.deadline_date)
        self.assertTrue(
            self.registry('calculation.method').read(
                self.cr,
                self.uid,
                method_id,
                ['active'])['active'])
        self.assertFalse(
            self.registry('retrocession').read(
                self.cr,
                self.uid,
                retro_id,
                ['active'])['active'])

    def test_retro_instance_on_assemblies(self):
        '''
            If a mandate category has a retrocession mode, all assemblies
            impacted should have
            a retrocession management instance specified
        '''
        mandate_category_id = self.ref(
            '%s.sta_assembly_category_11' %
            self._module_ns)
        self.assertRaises(orm.except_orm,
                          self.registry('mandate.category').write,
                          self.cr,
                          self.uid,
                          mandate_category_id,
                          {'retrocession_mode': 'month'})

    def test_mandate_reference(self):
        '''
            All state and external mandates should have a reference
        '''
        mandate_ids = self.registry('sta.mandate').search(
            self.cr, self.uid, [
                ('reference', '=', False)])
        self.assertEqual(len(mandate_ids), 0)
        mandate_ids = self.registry('ext.mandate').search(
            self.cr, self.uid, [
                ('reference', '=', False)])
        self.assertEqual(len(mandate_ids), 0)

    def test_ext_mandates(self):
        '''
            Test mandates
        '''
        rule_pool = self.registry('calculation.rule')
        mandate_id = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)

        # Retrocession mode should be monthly
        retrocession_mode = self.registry('ext.mandate').read(
            self.cr,
            self.uid,
            mandate_id,
            ['retrocession_mode'])['retrocession_mode']
        self.assertEqual(retrocession_mode, 'month')

        # Check if fixed rules has been copied from method to mandate
        rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('ext_mandate_id', '=', mandate_id), ('type', '=', 'fixed')])
        self.assertEqual(len(rule_ids), 2)

        # Check changing mandate category and assembly changes rules
        assembly_id = self.ref('%s.ext_assembly_01' % self._module_ns)
        mandate_cat_id = self.ref('%s.mc_administrateur' % self._module_ns)
        self.registry('ext.mandate').write(
            self.cr, self.uid, mandate_id, {
                'mandate_category_id': mandate_cat_id,
                'ext_assembly_id': assembly_id})
        rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('ext_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 1)
        assembly_id = self.ref('%s.ext_assembly_02' % self._module_ns)
        mandate_cat_id = self.ref('%s.mc_membre_effectif_ag' % self._module_ns)
        self.registry('ext.mandate').write(
            self.cr, self.uid, mandate_id, {
                'mandate_category_id': mandate_cat_id,
                'ext_assembly_id': assembly_id})

    def test_sta_mandates(self):
        '''
            Test mandates
        '''
        rule_pool = self.registry('calculation.rule')
        mandate_id = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)

        # Retrocession mode should be yearly
        retrocession_mode = self.registry('sta.mandate').read(
            self.cr,
            self.uid,
            mandate_id,
            ['retrocession_mode'])['retrocession_mode']
        self.assertEqual(retrocession_mode, 'year')

        # Check if fixed rules has been copied from method to mandate
        rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('sta_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 2)

        # Check changing mandate category changes rules
        mandate_cat_id = self.ref('%s.mc_administrateur' % self._module_ns)
        self.registry('sta.mandate').write(
            self.cr, self.uid, mandate_id, {
                'mandate_category_id': mandate_cat_id})
        rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('sta_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 1)
        mandate_cat_id = self.ref(
            '%s.mc_conseiller_communal' % self._module_ns)
        self.registry('sta.mandate').write(
            self.cr, self.uid, mandate_id, {
                'mandate_category_id': mandate_cat_id})

        # Check changing assembly changes rules
        assembly_id = self.ref('%s.sta_assembly_01' % self._module_ns)
        self.registry('sta.mandate').write(
            self.cr, self.uid, mandate_id, {
                'sta_assembly_id': assembly_id})
        rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('sta_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 1)
        assembly_id = self.ref('%s.sta_assembly_03' % self._module_ns)
        self.registry('sta.mandate').write(
            self.cr, self.uid, mandate_id, {
                'sta_assembly_id': assembly_id})

    def test_retrocession_unicity(self):
        '''
            Test impossibility to create several retrocession for the same
            mandate at the same period
        '''
        mandate_id = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)
        data = dict(ext_mandate_id=mandate_id,
                    month='05', year=int(self.year),
                    )
        self.assertRaises(
            orm.except_orm,
            self.registry('retrocession').create,
            self.cr,
            self.uid,
            data)

        mandate_id = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)
        data = dict(sta_mandate_id=mandate_id,
                    year=int(self.year),
                    )
        self.assertRaises(
            orm.except_orm,
            self.registry('retrocession').create,
            self.cr,
            self.uid,
            data)

    def test_regulation_retrocession(self):
        '''
            Test regulation retrocession
        '''
        mandate_id = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)

        # Try to create a regulation retrocession for May
        data = {'ext_mandate_id': mandate_id,
                'month': '05',
                'year': int(self.year)
                }
        self.assertRaises(
            orm.except_orm,
            self.registry('retrocession').create,
            self.cr,
            self.uid,
            data)

        # Create a regulation retrocession for December
        data = {'ext_mandate_id': mandate_id,
                'month': '12',
                'year': int(self.year)
                }

        self.registry('retrocession').create(self.cr, self.uid, data)
        self.assertRaises(
            orm.except_orm,
            self.registry('retrocession').create,
            self.cr,
            self.uid,
            data)

        data['is_regulation'] = True
        retro_id = self.registry('retrocession').create(
            self.cr, self.uid, data)
        self.assertNotEqual(retro_id, False)
