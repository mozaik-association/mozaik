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
from anybox.testing.openerp import SharedSetupTransactionCase


class test_report_payment_certificate_wizard(SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        '../../ficep_structure/tests/data/structure_data.xml',
        '../../ficep_mandate/tests/data/mandate_data.xml',
        'data/retrocession_data.xml',
    )

    _module_ns = 'ficep_retrocession'

    def test_report_payment_certificate_wizard_ext_mandate(self):

        mandate_id1 = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)
        mandate_id2 = self.ref('%s.extm_paul_adm' % self._module_ns)
        retro_id = self.ref('%s.retro_paul_adm_mai_2014' % self._module_ns)
        retro_pool = self.registry('retrocession')
        rule_pool = self.registry('calculation.rule')

        fixed_rule_ids = rule_pool.search(self.cr, self.uid,
                                          [('retrocession_id', '=', retro_id),
                                           ('type', '=', 'fixed'),
                                           ('is_deductible', '=', False)])

        wizard_pool = self.registry('report.payment.certificate.wizard')
        context = dict(active_model='ext.mandate',
                     active_ids=[mandate_id1, mandate_id2])

        data = wizard_pool.default_get(self.cr, self.uid, [], context=context)
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
        self.assertEqual(res['total_certificate'], 0)

        rule_pool.write(self.cr, self.uid, fixed_rule_ids, {'amount': 100})
        retro_pool.write(self.cr, self.uid, retro_id,
                                            {'amount_reconcilied': 3.4})
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
        self.assertEqual(res['total_certificate'], 1)

    def test_report_payment_certificate_wizard_sta_mandate(self):

        mandate_id1 = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)
        mandate_id2 = self.ref('%s.stam_paul_gouverneur' % self._module_ns)
        retro_id = self.ref('%s.retro_paul_gouv_2014' % self._module_ns)
        retro_pool = self.registry('retrocession')
        rule_pool = self.registry('calculation.rule')

        fixed_rule_ids = rule_pool.search(self.cr, self.uid,
                                          [('retrocession_id', '=', retro_id),
                                           ('type', '=', 'fixed'),
                                           ('is_deductible', '=', False)])

        wizard_pool = self.registry('report.payment.certificate.wizard')
        context = dict(active_model='sta.mandate',
                     active_ids=[mandate_id1, mandate_id2])

        data = wizard_pool.default_get(self.cr, self.uid, [], context=context)
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
        self.assertEqual(res['total_certificate'], 0)

        rule_pool.write(self.cr, self.uid, fixed_rule_ids, {'amount': 100})
        retro_pool.write(self.cr, self.uid, retro_id,
                                            {'amount_reconcilied': 3.4})
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
        self.assertEqual(res['total_certificate'], 1)
