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

    def test_monthly_retrocession_factory_wizard(self):

        mandate_id = self.ref('%s.extm_jacques_membre_ag' % self._module_ns)

        wizard_pool = self.registry('retrocession.factory.wizard')
        context = dict(active_model='ext.mandate',
                       active_ids=[mandate_id])

        data = wizard_pool.default_get(self.cr, self.uid, [], context=context)
        data.update({'month': '05', 'year': int(self.year)})

        wiz_id = wizard_pool.create(self.cr, self.uid, data, context=context)
        res = wizard_pool.mandate_selection_analysis(
            self.cr,
            self.uid,
            data['month'],
            data['year'],
            data['model'],
            eval(
                data['mandate_ids']))

        self.assertEqual(res['monthly_count'], 0)
        self.assertEqual(res['yearly_count'], 0)
        self.assertEqual(res['monthly_duplicates'], 1)
        self.assertEqual(res['yearly_duplicates'], 0)
        self.assertEqual(res['total_retrocession'], 0)

        data.update({'month': '06'})
        wizard_pool.write(self.cr, self.uid, [wiz_id], data, context=context)
        res = wizard_pool.mandate_selection_analysis(
            self.cr,
            self.uid,
            data['month'],
            data['year'],
            data['model'],
            eval(
                data['mandate_ids']))

        self.assertEqual(res['monthly_count'], 1)
        self.assertEqual(res['yearly_count'], 0)
        self.assertEqual(res['monthly_duplicates'], 0)
        self.assertEqual(res['yearly_duplicates'], 0)
        self.assertEqual(res['total_retrocession'], 1)

        wizard_pool.generate_retrocessions(self.cr, self.uid, [wiz_id])

        retro_ids = self.registry('retrocession').search(
            self.cr, self.uid, [
                ('ext_mandate_id', '=', mandate_id),
                ('month', '=', data['month']),
                ('year', '=', data['year'])])
        self.assertEqual(len(retro_ids), 1)

    def test_yearly_retrocession_factory_wizard(self):

        mandate_id = self.ref('%s.stam_jacques_bourgmestre' % self._module_ns)

        wizard_pool = self.registry('retrocession.factory.wizard')
        context = dict(active_model='sta.mandate',
                       active_ids=[mandate_id])

        data = wizard_pool.default_get(self.cr, self.uid, [], context=context)
        data.update({'year': int(self.year)})

        wiz_id = wizard_pool.create(self.cr, self.uid, data, context=context)
        res = wizard_pool.mandate_selection_analysis(
            self.cr,
            self.uid,
            data['month'],
            data['year'],
            data['model'],
            eval(
                data['mandate_ids']))

        self.assertEqual(res['monthly_count'], 0)
        self.assertEqual(res['yearly_count'], 0)
        self.assertEqual(res['monthly_duplicates'], 0)
        self.assertEqual(res['yearly_duplicates'], 1)
        self.assertEqual(res['total_retrocession'], 0)

        data.update({'year': int(self.year)+1})
        wizard_pool.write(self.cr, self.uid, [wiz_id], data, context=context)
        res = wizard_pool.mandate_selection_analysis(
            self.cr,
            self.uid,
            data['month'],
            data['year'],
            data['model'],
            eval(data['mandate_ids']))

        self.assertEqual(res['monthly_count'], 0)
        self.assertEqual(res['yearly_count'], 1)
        self.assertEqual(res['monthly_duplicates'], 0)
        self.assertEqual(res['yearly_duplicates'], 0)
        self.assertEqual(res['total_retrocession'], 1)

        wizard_pool.generate_retrocessions(self.cr, self.uid, [wiz_id])

        retro_ids = self.registry('retrocession').search(
            self.cr, self.uid, [
                ('sta_mandate_id', '=', mandate_id),
                ('year', '=', data['year']),
                ('month', '=', False)])
        self.assertEqual(len(retro_ids), 1)
