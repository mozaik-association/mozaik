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
from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.osv import fields
from openerp.addons.ficep_base import testtool

_logger = logging.getLogger(__name__)


class test_retrocession(SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        '../../ficep_structure/tests/data/structure_data.xml',
        '../../ficep_mandate/tests/data/mandate_data.xml',
        'data/retrocession_data.xml',
    )

    _module_ns = 'ficep_retrocession'

    def setUp(self):
        super(test_retrocession, self).setUp()

    def test_fractionation_invalidate(self):
        '''
            Test automatic invalidation of lines of a given fractionation
        '''
        fractionation_pool = self.registry('fractionation')
        fractionation_01 = self.browse_ref('%s.f_sample_01' % self._module_ns)

        fractionation_pool.action_invalidate(self.cr, self.uid, [fractionation_01.id])

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
        int_power_level_02_id = self.ref('%s.int_power_level_02' % self._module_ns)
        data = dict(fractionation_id=fractionation_02_id,
                    power_level_id=int_power_level_02_id,
                    percentage=142)

        with testtool.disable_log_error(self.cr):
            self.assertRaises(psycopg2.IntegrityError, self.registry('fractionation.line').create, self.cr, self.uid, data)

    def test_unicity_fractionation_line(self):
        '''
            Test reference to a power level must unique within a fractionation
        '''
        fractionation_02_id = self.ref('%s.f_sample_02' % self._module_ns)
        int_power_level_01_id = self.ref('ficep_structure.int_power_level_01')
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
        method_01 = self.browse_ref('%s.cm_sample_02' % self._module_ns)

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
        retro_id = self.ref('%s.retro_paul_ag_mai_2014' % self._module_ns)
        partner_id = self.ref('%s.res_partner_paul' % self._module_ns)

        self.registry('res.partner').write(self.cr, self.uid, [partner_id], {'active': False,
                                                                             'expire_date': fields.datetime.now(), }, context=None)

        self.assertFalse(self.registry('ext.mandate').read(self.cr, self.uid, mandate_id, ['active'])['active'])
        self.assertTrue(self.registry('calculation.method').read(self.cr, self.uid, method_id, ['active'])['active'])
        self.assertFalse(self.registry('retrocession').read(self.cr, self.uid, retro_id, ['active'])['active'])

    def test_retro_instance_on_assemblies(self):
        '''
            If a mandate category has a invoicing type, all assemblies impacted should have
            a retrocession management instance specified
        '''
        mandate_category_id = self.ref('%s.sta_assembly_category_11' % self._module_ns)
        self.assertRaises(orm.except_orm, self.registry('mandate.category').write, self.cr, self.uid, mandate_category_id, {'invoice_type': 'month'})

    def test_mandate_reference(self):
        '''
            All state and external mandates should have a reference
        '''
        mandate_ids = self.registry('sta.mandate').search(self.cr, self.uid, [('reference', '=', False)])
        self.assertEqual(len(mandate_ids), 0)
        mandate_ids = self.registry('ext.mandate').search(self.cr, self.uid, [('reference', '=', False)])
        self.assertEqual(len(mandate_ids), 0)

    def test_ext_mandates(self):
        '''
            Test mandates
        '''
        rule_pool = self.registry('calculation.rule')
        mandate_id = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)

        '''
            Invoicing type should be monthly
        '''
        invoicing_type = self.registry('ext.mandate').read(self.cr, self.uid, mandate_id, ['invoice_type'])['invoice_type']
        self.assertEqual(invoicing_type, 'month')

        '''
            Check if fixed rules has been copied from method to mandate
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('ext_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 2)

        '''
            Check changing mandate category changes rules
        '''
        mandate_cat_id = self.ref('%s.mc_administrateur' % self._module_ns)
        self.registry('ext.mandate').write(self.cr, self.uid, mandate_id, {'mandate_category_id': mandate_cat_id})
        rule_ids = rule_pool.search(self.cr, self.uid, [('ext_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 0)
        mandate_cat_id = self.ref('%s.mc_membre_effectif_ag' % self._module_ns)
        self.registry('ext.mandate').write(self.cr, self.uid, mandate_id, {'mandate_category_id': mandate_cat_id})

        '''
            Check changing assembly changes rules
        '''
        assembly_id = self.ref('%s.ext_assembly_02' % self._module_ns)
        self.registry('ext.mandate').write(self.cr, self.uid, mandate_id, {'ext_assembly_id': assembly_id})
        rule_ids = rule_pool.search(self.cr, self.uid, [('ext_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 1)
        assembly_id = self.ref('%s.ext_assembly_01' % self._module_ns)
        self.registry('ext.mandate').write(self.cr, self.uid, mandate_id, {'ext_assembly_id': assembly_id})

    def test_sta_mandates(self):
        '''
            Test mandates
        '''
        rule_pool = self.registry('calculation.rule')
        mandate_id = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)

        '''
            Invoicing type should be yearly
        '''
        invoicing_type = self.registry('sta.mandate').read(self.cr, self.uid, mandate_id, ['invoice_type'])['invoice_type']
        self.assertEqual(invoicing_type, 'year')

        '''
            Check if fixed rules has been copied from method to mandate
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('sta_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 2)

        '''
            Check changing mandate category changes rules
        '''
        mandate_cat_id = self.ref('%s.mc_administrateur' % self._module_ns)
        self.registry('sta.mandate').write(self.cr, self.uid, mandate_id, {'mandate_category_id': mandate_cat_id})
        rule_ids = rule_pool.search(self.cr, self.uid, [('sta_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 0)
        mandate_cat_id = self.ref('%s.mc_conseiller_communal' % self._module_ns)
        self.registry('sta.mandate').write(self.cr, self.uid, mandate_id, {'mandate_category_id': mandate_cat_id})

        '''
            Check changing assembly changes rules
        '''
        assembly_id = self.ref('%s.sta_assembly_01' % self._module_ns)
        self.registry('sta.mandate').write(self.cr, self.uid, mandate_id, {'sta_assembly_id': assembly_id})
        rule_ids = rule_pool.search(self.cr, self.uid, [('sta_mandate_id', '=', mandate_id)])
        self.assertEqual(len(rule_ids), 1)
        assembly_id = self.ref('%s.sta_assembly_03' % self._module_ns)
        self.registry('sta.mandate').write(self.cr, self.uid, mandate_id, {'sta_assembly_id': assembly_id})

    def test_retrocession_unicity(self):
        '''
            Test impossibility to create several retrocession for the same mandate at the same period
        '''
        mandate_id = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)
        data = dict(ext_mandate_id=mandate_id,
                    month=5, year=2014,
                    )
        self.assertRaises(orm.except_orm, self.registry('retrocession').create, self.cr, self.uid, data)

        mandate_id = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)
        data = dict(sta_mandate_id=mandate_id,
                    year=2014,
                    )
        self.assertRaises(orm.except_orm, self.registry('retrocession').create, self.cr, self.uid, data)

    def test_retrocession_ext_mandate_process(self):
        '''
            Test retrocessions
        '''
        rule_pool = self.registry('calculation.rule')
        retro_pool = self.registry('retrocession')
        retro_id = self.ref('%s.retro_jacques_ag_mai_2014' % self._module_ns)
        mandate_id = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)

        '''
            Check if variable rules has been copied from method to retrocession
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('retrocession_id', '=', retro_id)])
        self.assertEqual(len(rule_ids), 1)

        '''
            Setting some amounts on fixed rules should invoke retrocession calculation
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('ext_mandate_id', '=', mandate_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'amount': 100})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 3.40)
        self.assertEqual(amounts['amount_total'], 3.40)

        '''
            Setting some amounts on variable rules should invoke retrocession calculation
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('retrocession_id', '=', retro_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'amount': 100})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_variable', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 3.40)
        self.assertEqual(amounts['amount_variable'], 0.75)
        self.assertEqual(amounts['amount_total'], 4.15)

        '''
            Changing percentage of fixed rules should affect retrocession computation
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('ext_mandate_id', '=', mandate_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'percentage': 0.25})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 0.50)
        self.assertEqual(amounts['amount_total'], 1.25)

        '''
            Changing percentage of variable rules should affect retrocession computation
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('retrocession_id', '=', retro_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'percentage': 5})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_variable', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 0.50)
        self.assertEqual(amounts['amount_variable'], 5)
        self.assertEqual(amounts['amount_total'], 5.5)

        '''
            After validating retrocession, no computation should occurs
        '''
        retro_pool.action_validate(self.cr, self.uid, [retro_id])
        retro_state = retro_pool.read(self.cr, self.uid, retro_id, ['state'])['state']
        self.assertEqual(retro_state, 'validated')

        rule_ids = rule_pool.search(self.cr, self.uid, [('ext_mandate_id', '=', mandate_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'percentage': 0.55})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 0.50)
        self.assertEqual(amounts['amount_total'], 5.5)

        '''
            Fixed rules should have been copied on retrocession to keep computation basis history
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('retrocession_id', '=', retro_id), ('type', '=', 'variable')])
        self.assertEqual(len(rule_ids), 1)

    def test_retrocession_sta_mandate_process(self):
        '''
            Test retrocessions
        '''
        rule_pool = self.registry('calculation.rule')
        retro_pool = self.registry('retrocession')
        retro_id = self.ref('%s.retro_jacques_bourg_mai_2014' % self._module_ns)
        mandate_id = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)

        '''
            Check if variable rules has been copied from method to retrocession
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('retrocession_id', '=', retro_id)])
        self.assertEqual(len(rule_ids), 1)

        '''
            Setting some amounts on fixed rules should invoke retrocession calculation
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('sta_mandate_id', '=', mandate_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'amount': 100})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 3.40)
        self.assertEqual(amounts['amount_total'], 3.40)

        '''
            Setting some amounts on variable rules should invoke retrocession calculation
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('retrocession_id', '=', retro_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'amount': 100})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_variable', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 3.40)
        self.assertEqual(amounts['amount_variable'], 0.75)
        self.assertEqual(amounts['amount_total'], 4.15)

        '''
            Changing percentage of fixed rules should affect retrocession computation
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('sta_mandate_id', '=', mandate_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'percentage': 0.25})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 0.50)
        self.assertEqual(amounts['amount_total'], 1.25)

        '''
            Changing percentage of variable rules should affect retrocession computation
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('retrocession_id', '=', retro_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'percentage': 5})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_variable', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 0.50)
        self.assertEqual(amounts['amount_variable'], 5)
        self.assertEqual(amounts['amount_total'], 5.5)

        '''
            After validating retrocession, no computation should occurs
        '''
        retro_pool.action_validate(self.cr, self.uid, [retro_id])
        retro_state = retro_pool.read(self.cr, self.uid, retro_id, ['state'])['state']
        self.assertEqual(retro_state, 'validated')

        rule_ids = rule_pool.search(self.cr, self.uid, [('sta_mandate_id', '=', mandate_id)])
        rule_pool.write(self.cr, self.uid, rule_ids, {'percentage': 0.55})
        amounts = retro_pool.read(self.cr, self.uid, retro_id, ['amount_fixed', 'amount_total'])
        self.assertEqual(amounts['amount_fixed'], 0.50)
        self.assertEqual(amounts['amount_total'], 5.5)

        '''
            Fixed rules should have been copied on retrocession to keep computation basis history
        '''
        rule_ids = rule_pool.search(self.cr, self.uid, [('retrocession_id', '=', retro_id), ('type', '=', 'variable')])
        self.assertEqual(len(rule_ids), 1)
