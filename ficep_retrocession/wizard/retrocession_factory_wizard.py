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
from openerp.osv import orm, fields
import datetime


class retrocession_factory_wizard(orm.TransientModel):
    _name = "retrocession.factory.wizard"

    _active_model = None
    _mandate_key = None
    _mandate_ids = None
    _selected_mandate_ids = None
    _month = None
    _year = None
    _cache_dict = None

    _columns = {
        'month': fields.selection(fields.date.MONTHS, 'Month', size=128, select=True),
        'year': fields.char('Year', size=128, select=True, required=True),
        'mandate_selected': fields.integer('Mandate selected'),
        'yearly_count': fields.integer('Yearly retrocession(s) to create'),
        'yearly_duplicates': fields.integer('Yearly retrocession(s) already existing'),
        'monthly_count': fields.integer('Monthly retrocession(s) to create'),
        'monthly_duplicates': fields.integer('Monthly retrocession(s) already existing'),
        'total_retrocession': fields.integer('Total retrocession to create'),
    }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        res = {}
        context = context or {}

        today = datetime.date.today()
        first = datetime.date(day=1, month=today.month, year=today.year)
        lastMonth = first - datetime.timedelta(days=1)
        res['month'] = lastMonth.strftime("%m")
        res['year'] = lastMonth.strftime("%Y")

        self._active_model = context.get('active_model', False)
        if self._active_model == 'sta.mandate':
            self._mandate_key = 'sta_mandate_id'
        elif self._active_model == 'ext.mandate':
            self._mandate_key = 'ext_mandate_id'

        self._selected_mandate_ids = context.get('active_ids') or (context.get('active_id') and [context.get('active_id')]) or []

        return res

    def mandate_selection_analysis(self, cr, uid, month, year, context=None):
        """
        ===============
        mandate_selection_analysis
        ==============)
        Analyse mandate selection and give an overview of expected results
        """
        res = {}
        rejected_ids = []
        yearly_count, yearly_duplicates, monthly_count, monthly_duplicates = 0, 0, 0, 0
        for mandate_data in self.pool.get(self._active_model).read(cr, uid, self._selected_mandate_ids,
                                                                   ['invoice_type', 'end_date', 'deadline_date', 'calculation_method_id'], context=context):
            if mandate_data['end_date'] \
            or mandate_data['deadline_date'] <= fields.date.today() \
            or mandate_data['invoice_type'] not in ['month', 'year']\
            or not mandate_data['calculation_method_id']:
                rejected_ids.append(mandate_data['id'])
                continue

            if mandate_data['invoice_type'] == 'month':
                duplicate_ids = self.pool.get('retrocession').search(cr, uid, [(self._mandate_key, '=', mandate_data['id']),
                                                                              ('month', '=', month),
                                                                              ('year', '=', year)], context=context)

                if not duplicate_ids:
                    monthly_count += 1
                else:
                    monthly_duplicates += 1

            elif mandate_data['invoice_type'] == 'year':
                duplicate_ids = self.pool.get('retrocession').search(cr, uid, [(self._mandate_key, '=', mandate_data['id']),
                                                                               ('year', '=', year)], context=context)
                if not duplicate_ids:
                    yearly_count += 1
                else:
                    yearly_duplicates += 1

        self._mandate_ids = list(set(self._selected_mandate_ids) - set(rejected_ids))
        res['mandate_selected'] = len(self._selected_mandate_ids)
        res['total_retrocession'] = yearly_count + monthly_count
        res['yearly_count'] = yearly_count
        res['yearly_duplicates'] = yearly_duplicates
        res['monthly_count'] = monthly_count
        res['monthly_duplicates'] = monthly_duplicates

        self._cache_dict = res
        return res

    def onchange_month_year(self, cr, uid, ids, month, year, context=None):
        res = {}
        if month != self._month or year != self._year:
            self._month = month
            self._year = year
            res['value'] = self.mandate_selection_analysis(cr, uid, month, year, context=context)
        else:
            res['value'] = self._cache_dict

        return res

    def generate_retrocessions(self, cr, uid, ids, context=None):
        """
        =======================
        generate_retrocessions
        =======================
        Generate retrocessions for valid selected mandates
        """
        wizard = self.browse(cr, uid, ids, context=context)[0]
        for mandate_id in self._mandate_ids:
            data = dict(month=wizard.month,
                      year=wizard.year)

            data[self._mandate_key] = mandate_id
            self.pool.get('retrocession').create(cr, uid, data, context=context)
