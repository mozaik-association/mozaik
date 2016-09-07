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
from anybox.testing.openerp import SharedSetupTransactionCase


class test_report_retrocession_wizard(SharedSetupTransactionCase):

    _data_files = (
        '../../l10n_mozaik/data/account_template.xml',
        '../../l10n_mozaik/data/account_chart_template.xml',
        '../../l10n_mozaik/data/account_installer.xml',
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        '../../mozaik_mandate/tests/data/mandate_data.xml',
        'data/retrocession_data.xml',
    )

    _module_ns = 'mozaik_retrocession'

    def setUp(self):
        super(test_report_retrocession_wizard, self).setUp()
        self.year = (datetime.today() - relativedelta(years=1)).strftime('%Y')

    def test_report_payment_certificate_ext_mandate(self):

        mandate_id1 = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)
        mandate_id2 = self.ref('%s.extm_paul_adm' % self._module_ns)
        retro_id = self.ref('%s.retro_paul_adm_mai_20xx' % self._module_ns)
        retro_pool = self.registry('retrocession')
        rule_pool = self.registry('calculation.rule')

        fixed_rule_ids = rule_pool.search(self.cr, self.uid,
                                          [('retrocession_id', '=', retro_id),
                                           ('type', '=', 'fixed'),
                                           ('is_deductible', '=', False)])

        wizard_pool = self.registry('report.retrocession.wizard')
        context = dict(active_model='ext.mandate',
                       active_ids=[mandate_id1, mandate_id2])

        data = wizard_pool.default_get(self.cr, self.uid, [], context=context)
        data['year'] = self.year
        data['report'] = 'certificates'
        wizard_pool.create(self.cr, self.uid, data, context=context)
        res = wizard_pool.mandate_selection_analysis(self.cr,
                                                     self.uid,
                                                     data['year'],
                                                     data['model'],
                                                     eval(data['mandate_ids']))

        self.assertEqual(res['monthly_count'], 2)
        self.assertEqual(res['yearly_count'], 0)
        self.assertEqual(res['monthly_print'], 0)
        self.assertEqual(res['yearly_print'], 0)
        self.assertEqual(res['total_mandates'], 0)

        rule_pool.write(self.cr, self.uid, fixed_rule_ids, {'amount': 100})
        retro_pool.write(self.cr, self.uid, retro_id,
                         {'amount_paid': 3.4})
        retro_pool.action_done(self.cr, self.uid, [retro_id])

        res = wizard_pool.mandate_selection_analysis(self.cr,
                                                     self.uid,
                                                     data['year'],
                                                     data['model'],
                                                     eval(data['mandate_ids']))

        self.assertEqual(res['monthly_count'], 2)
        self.assertEqual(res['yearly_count'], 0)
        self.assertEqual(res['monthly_print'], 1)
        self.assertEqual(res['yearly_print'], 0)
        self.assertEqual(res['total_mandates'], 1)

    def test_report_payment_certificate_sta_mandate(self):

        mandate_id1 = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)
        mandate_id2 = self.ref('%s.stam_paul_gouverneur' % self._module_ns)
        retro_id = self.ref('%s.retro_paul_gouv_20xx' % self._module_ns)
        retro_pool = self.registry('retrocession')
        rule_pool = self.registry('calculation.rule')

        fixed_rule_ids = rule_pool.search(self.cr, self.uid,
                                          [('retrocession_id', '=', retro_id),
                                           ('type', '=', 'fixed'),
                                           ('is_deductible', '=', False)])

        wizard_pool = self.registry('report.retrocession.wizard')
        context = dict(active_model='sta.mandate',
                       active_ids=[mandate_id1, mandate_id2])

        data = wizard_pool.default_get(self.cr, self.uid, [], context=context)
        data['year'] = self.year
        data['report'] = 'certificates'
        wizard_pool.create(self.cr, self.uid, data, context=context)
        res = wizard_pool.mandate_selection_analysis(self.cr,
                                                     self.uid,
                                                     data['year'],
                                                     data['model'],
                                                     eval(data['mandate_ids']))

        self.assertEqual(res['monthly_count'], 0)
        self.assertEqual(res['yearly_count'], 2)
        self.assertEqual(res['monthly_print'], 0)
        self.assertEqual(res['yearly_print'], 0)
        self.assertEqual(res['total_mandates'], 0)

        rule_pool.write(self.cr, self.uid, fixed_rule_ids, {'amount': 100})
        retro_pool.write(self.cr, self.uid, retro_id,
                         {'amount_paid': 3.4})
        retro_pool.action_done(self.cr, self.uid, [retro_id])

        res = wizard_pool.mandate_selection_analysis(self.cr,
                                                     self.uid,
                                                     data['year'],
                                                     data['model'],
                                                     eval(data['mandate_ids']))

        self.assertEqual(res['monthly_count'], 0)
        self.assertEqual(res['yearly_count'], 2)
        self.assertEqual(res['monthly_print'], 0)
        self.assertEqual(res['yearly_print'], 1)
        self.assertEqual(res['total_mandates'], 1)

    def test_report_fractionations_ext_mandate(self):
        federal_inst = self.browse_ref('mozaik_structure.int_instance_01')
        liege_inst = self.browse_ref('%s.int_instance_03'
                                     % self._module_ns)
        huy_waremme_inst = self.browse_ref('%s.int_instance_04'
                                           % self._module_ns)
        huy_inst = self.browse_ref('%s.int_instance_05'
                                   % self._module_ns)
        orey_inst = self.browse_ref('%s.int_instance_06'
                                    % self._module_ns)
        wanze_inst = self.browse_ref('%s.int_instance_07'
                                     % self._module_ns)

        federal_pl_id = self.ref('mozaik_structure.int_power_level_01')
        provincial_pl_id = self.ref('%s.int_power_level_03'
                                    % self._module_ns)
        regional_pl_id = self.ref('%s.int_power_level_04'
                                  % self._module_ns)
        local_pl_id = self.ref('%s.int_power_level_05'
                               % self._module_ns)

        mandate_id1 = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)
        mandate_id2 = self.ref('%s.extm_paul_membre_ag' % self._module_ns)
        mandate_id3 = self.ref('%s.extm_marc_membre_ag' % self._module_ns)
        mandate_ids = [mandate_id1, mandate_id2, mandate_id3]

        wiz_id = self.ref('%s.pcmn_mozaik' % self._module_ns)
        self.registry('wizard.multi.charts.accounts').auto_execute(
            self.cr, self.uid, [wiz_id])
        wizard_pool = self.registry('report.retrocession.wizard')
        context = dict(active_model='ext.mandate',
                       active_ids=mandate_ids)

        data = wizard_pool.default_get(self.cr, self.uid, [], context=context)
        data['year'] = self.year
        data['report'] = 'fractionations'
        wizard_pool.create(self.cr, self.uid, data, context=context)

        res = wizard_pool.mandate_selection_analysis(
            self.cr, self.uid,
            data['year'], data['model'], eval(data['mandate_ids']))
        self.assertEqual(res['monthly_count'], 3)
        self.assertEqual(res['yearly_count'], 0)
        self.assertEqual(res['monthly_print'], 0)
        self.assertEqual(res['yearly_print'], 0)
        self.assertEqual(res['total_mandates'], 0)

        helper_pool = self.registry('retrocession.helper')
        retro_ids = []
        retro_ids.append(self.ref('%s.retro_paul_ag_january_20xx'
                                  % self._module_ns))
        retro_ids.append(self.ref('%s.retro_marc_ag_january_20xx'
                                  % self._module_ns))
        retro_ids.append(self.ref('%s.retro_jacques_ag_january_20xx'
                                  % self._module_ns))
        helper_pool.create_fiscal_year(self.cr, self.uid, self.year)
        helper_pool.validate_retrocession_with_accounting(
            self.cr,
            self.uid,
            retro_ids)

        res = wizard_pool.mandate_selection_analysis(self.cr,
                                                     self.uid,
                                                     data['year'],
                                                     data['model'],
                                                     eval(data['mandate_ids']))
        self.assertEqual(res['monthly_count'], 3)
        self.assertEqual(res['yearly_count'], 0)
        self.assertEqual(res['monthly_print'], 3)
        self.assertEqual(res['yearly_print'], 0)
        self.assertEqual(res['total_mandates'], 3)

        inst_data, mand_data = wizard_pool._get_fractionation_data(
            self.cr,
            self.uid,
            mandate_ids,
            'ext.mandate',
            'ext.assembly',
            int(self.year), {})

        expected_result = {
            'Unfractioned': {
                'Instance': 'Unfractioned Amount',
                'Amount': 227.26,
                'Power Level': ''},
            federal_inst.id: {
                'Instance': federal_inst.name,
                'Amount': 1363.5,
                'Power Level': federal_inst.power_level_id.name},
            liege_inst.id: {
                'Instance': liege_inst.name,
                'Amount': 227.25,
                'Power Level': liege_inst.power_level_id.name},
            huy_waremme_inst.id: {
                'Instance': huy_waremme_inst.name,
                'Amount': 68.17,
                'Power Level': huy_waremme_inst.power_level_id.name},
            huy_inst.id: {
                'Instance': huy_inst.name,
                'Amount': 164.47,
                'Power Level': huy_inst.power_level_id.name},
            orey_inst.id: {
                'Instance': orey_inst.name,
                'Amount': 164.47,
                'Power Level': orey_inst.power_level_id.name},
            wanze_inst.id: {
                'Instance': wanze_inst.name,
                'Amount': 57.38,
                'Power Level': wanze_inst.power_level_id.name},
        }

        self.assertDictEqual(inst_data, expected_result)

        expected_result = {
            mandate_id1: {
                'Unfractioned': 96.75999999999999,
                federal_pl_id: {
                    'amount': 580.5,
                    'name': federal_inst.name,
                    'id': federal_inst.id
                },
                regional_pl_id: {
                    'amount': 29.02,
                    'name': huy_waremme_inst.name,
                    'id': huy_waremme_inst.id
                },
                provincial_pl_id: {
                    'amount': 96.75,
                    'name': liege_inst.name,
                    'id': liege_inst.id
                },
                local_pl_id: {
                    'amount': 164.47,
                    'name': huy_inst.name,
                    'id': huy_inst.id
                }

            },
            mandate_id2: {
                'Unfractioned': 33.74000000000001,
                federal_pl_id: {
                    'amount': 202.5,
                    'name': federal_inst.name,
                    'id': federal_inst.id
                },
                regional_pl_id: {
                    'amount': 10.13,
                    'name': huy_waremme_inst.name,
                    'id': huy_waremme_inst.id
                },
                provincial_pl_id: {
                    'amount': 33.75,
                    'name': liege_inst.name,
                    'id': liege_inst.id
                },
                local_pl_id: {
                    'amount': 57.38,
                    'name': wanze_inst.name,
                    'id': wanze_inst.id
                }

            },
            mandate_id3: {
                'Unfractioned': 96.75999999999999,
                federal_pl_id: {
                    'amount': 580.5,
                    'name': federal_inst.name,
                    'id': federal_inst.id
                },
                regional_pl_id: {
                    'amount': 29.02,
                    'name': huy_waremme_inst.name,
                    'id': huy_waremme_inst.id
                },
                provincial_pl_id: {
                    'amount': 96.75,
                    'name': liege_inst.name,
                    'id': liege_inst.id
                },
                local_pl_id: {
                    'amount': 164.47,
                    'name': orey_inst.name,
                    'id': orey_inst.id
                }

            },
        }

        for mandate_id in mandate_ids:
            split_dict = mand_data[mandate_id]['split']
            self.assertDictEqual(split_dict, expected_result[mandate_id])

        expected_result = list(set([federal_pl_id,
                                    regional_pl_id,
                                    provincial_pl_id,
                                    local_pl_id]))
        pl_ids = wizard_pool._extract_power_level_ids(self.cr,
                                                      self.uid,
                                                      mand_data,
                                                      {})
        self.assertListEqual(sorted(pl_ids), sorted(expected_result))

    def test_report_fractionations_sta_mandate(self):
        federal_inst = self.browse_ref('mozaik_structure.int_instance_01')
        liege_inst = self.browse_ref('%s.int_instance_03'
                                     % self._module_ns)
        huy_waremme_inst = self.browse_ref('%s.int_instance_04'
                                           % self._module_ns)
        huy_inst = self.browse_ref('%s.int_instance_05'
                                   % self._module_ns)

        federal_pl_id = self.ref('mozaik_structure.int_power_level_01')
        provincial_pl_id = self.ref('%s.int_power_level_03'
                                    % self._module_ns)
        regional_pl_id = self.ref('%s.int_power_level_04'
                                  % self._module_ns)
        local_pl_id = self.ref('%s.int_power_level_05'
                               % self._module_ns)

        mandate_id1 = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)
        mandate_ids = [mandate_id1]

        wiz_id = self.ref('%s.pcmn_mozaik' % self._module_ns)
        self.registry('wizard.multi.charts.accounts').auto_execute(
            self.cr, self.uid, [wiz_id])
        wizard_pool = self.registry('report.retrocession.wizard')
        context = dict(active_model='sta.mandate',
                       active_ids=mandate_ids)

        data = wizard_pool.default_get(self.cr, self.uid, [], context=context)
        data['year'] = self.year
        data['report'] = 'fractionations'
        wizard_pool.create(self.cr, self.uid, data, context=context)

        res = wizard_pool.mandate_selection_analysis(self.cr,
                                                     self.uid,
                                                     data['year'],
                                                     data['model'],
                                                     eval(data['mandate_ids']))
        self.assertEqual(res['monthly_count'], 0)
        self.assertEqual(res['yearly_count'], 1)
        self.assertEqual(res['monthly_print'], 0)
        self.assertEqual(res['yearly_print'], 0)
        self.assertEqual(res['total_mandates'], 0)

        helper_pool = self.registry('retrocession.helper')
        retro_ids = []
        retro_ids.append(self.ref('%s.retro_jacques_bourg_20xx'
                                  % self._module_ns))
        helper_pool.create_fiscal_year(self.cr, self.uid, self.year)
        helper_pool.validate_retrocession_with_accounting(
            self.cr,
            self.uid,
            retro_ids)

        res = wizard_pool.mandate_selection_analysis(self.cr,
                                                     self.uid,
                                                     data['year'],
                                                     data['model'],
                                                     eval(data['mandate_ids']))
        self.assertEqual(res['monthly_count'], 0)
        self.assertEqual(res['yearly_count'], 1)
        self.assertEqual(res['monthly_print'], 0)
        self.assertEqual(res['yearly_print'], 1)
        self.assertEqual(res['total_mandates'], 1)

        inst_data, mand_data = wizard_pool._get_fractionation_data(
            self.cr,
            self.uid,
            mandate_ids,
            'sta.mandate',
            'sta.assembly',
            int(self.year), {})

        expected_result = {
            'Unfractioned': {
                'Instance': 'Unfractioned Amount',
                'Amount': 96.75999999999999,
                'Power Level': ''},
            federal_inst.id: {
                'Instance': federal_inst.name,
                'Amount': 580.5,
                'Power Level': federal_inst.power_level_id.name},
            liege_inst.id: {
                'Instance': liege_inst.name,
                'Amount': 96.75,
                'Power Level': liege_inst.power_level_id.name},
            huy_waremme_inst.id: {
                'Instance': huy_waremme_inst.name,
                'Amount': 29.02,
                'Power Level': huy_waremme_inst.power_level_id.name},
            huy_inst.id: {
                'Instance': huy_inst.name,
                'Amount': 164.47,
                'Power Level': huy_inst.power_level_id.name},
        }

        self.assertDictEqual(inst_data, expected_result)

        expected_result = {
            mandate_id1: {
                'Unfractioned': 96.75999999999999,
                federal_pl_id: {
                    'amount': 580.5,
                    'name': federal_inst.name,
                    'id': federal_inst.id
                },
                regional_pl_id: {
                    'amount': 29.02,
                    'name': huy_waremme_inst.name,
                    'id': huy_waremme_inst.id
                },
                provincial_pl_id: {
                    'amount': 96.75,
                    'name': liege_inst.name,
                    'id': liege_inst.id
                },
                local_pl_id: {
                    'amount': 164.47,
                    'name': huy_inst.name,
                    'id': huy_inst.id
                }
            },
        }

        for mandate_id in mandate_ids:
            split_dict = mand_data[mandate_id]['split']
            self.assertDictEqual(split_dict, expected_result[mandate_id])

        expected_result = list(set([federal_pl_id,
                                    regional_pl_id,
                                    provincial_pl_id,
                                    local_pl_id]))
        pl_ids = wizard_pool._extract_power_level_ids(self.cr,
                                                      self.uid,
                                                      mand_data,
                                                      {})
        self.assertListEqual(sorted(pl_ids), sorted(expected_result))
