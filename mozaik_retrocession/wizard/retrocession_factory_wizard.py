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

import datetime

from openerp.osv import orm, fields
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


MANDATE_M2O = {
    'sta.mandate': 'sta_mandate_id',
    'ext.mandate': 'ext_mandate_id',
}


class retrocession_factory_wizard(orm.TransientModel):
    _name = "retrocession.factory.wizard"
    _description = 'Retrocessions Generator'

    _columns = {
        'model': fields.char('Model', size=128, required=True),
        'mandate_ids': fields.text('IDS', required=True),
        'month': fields.selection(fields.date.MONTHS, 'Month'),
        'year': fields.char('Year', size=128, required=True),
        'mandate_selected': fields.integer('Selected Mandates'),
        'yearly_count': fields.integer('Yearly Retrocessions to Create'),
        'yearly_duplicates': fields.integer(
            'Yearly Retrocessions Already Existing'),
        'monthly_count': fields.integer('Monthly Retrocessions to Create'),
        'monthly_duplicates': fields.integer(
            'Monthly Retrocessions Already Existing'),
        'total_retrocession': fields.integer(
            'Number of Retrocessions to Create'),
    }

    def default_get(self, cr, uid, flds, context=None):
        """
        To get default values for the object.
        """
        context = context or {}

        today = datetime.date.today()
        first = datetime.date(day=1, month=today.month, year=today.year)
        lastMonth = first - datetime.timedelta(days=1)
        model = context.get('active_model', False)
        if context.get('active_domain'):
            active_domain = context.get('active_domain')
            ids = self.pool.get(model).search(
                cr, uid, active_domain, context=context)
        elif context.get('active_ids'):
            ids = context.get('active_ids') or (
                context.get('active_id') and [
                    context.get('active_id')]) or []

        res = {
            'model': model,
            'mandate_ids': str(ids),
            'month': lastMonth.strftime("%m"),
            'year': lastMonth.strftime("%Y"),
            'mandate_selected': len(ids),
        }

        return res

    def mandate_selection_analysis(
            self,
            cr,
            uid,
            month,
            year,
            model,
            ids,
            mode='onchange',
            context=None):
        """
        ===============
        mandate_selection_analysis
        ==============)
        Analyse mandate selection and give an overview of expected results
        """
        mandate_key = MANDATE_M2O.get(model, False)
        rejected_ids = []
        yearly_count = 0
        yearly_duplicates = 0
        monthly_count = 0
        monthly_duplicates = 0
        for mandate_data in self.pool[model].read(cr,
                                                  uid,
                                                  ids,
                                                  ['retrocession_mode',
                                                   'end_date',
                                                   'deadline_date',
                                                   'calculation_method_id'],
                                                  context=context):
            if mandate_data['end_date'] or \
                    mandate_data['deadline_date'] <= fields.date.today() or \
                    mandate_data['retrocession_mode'] not in [
                        'month', 'year'] or\
                    not mandate_data['calculation_method_id']:
                rejected_ids.append(mandate_data['id'])
                continue

            if mandate_data['retrocession_mode'] == 'month':
                duplicate_ids = self.pool.get('retrocession').search(
                    cr,
                    uid,
                    [
                        (mandate_key,
                         '=',
                         mandate_data['id']),
                        ('month',
                         '=',
                         month),
                        ('year',
                         '=',
                         year),
                        ('is_regulation',
                         '=',
                         False)],
                    context=context)

                if not duplicate_ids:
                    monthly_count += 1
                else:
                    monthly_duplicates += 1

            elif mandate_data['retrocession_mode'] == 'year':
                duplicate_ids = self.pool.get('retrocession').search(
                    cr, uid, [
                        (mandate_key, '=', mandate_data['id']),
                        ('year', '=', year)],
                    context=context)
                if not duplicate_ids:
                    yearly_count += 1
                else:
                    yearly_duplicates += 1

        if mode == 'ids':
            res = list(set(ids) - set(rejected_ids))
        else:
            res = {
                'total_retrocession': yearly_count + monthly_count,
                'yearly_count': yearly_count,
                'yearly_duplicates': yearly_duplicates,
                'monthly_count': monthly_count,
                'monthly_duplicates': monthly_duplicates,
            }

        return res

    def onchange_month_year(
            self,
            cr,
            uid,
            ids,
            month,
            year,
            model,
            mandate_ids,
            context=None):
        return {
            'value': self.mandate_selection_analysis(
                cr,
                uid,
                month,
                year,
                model,
                eval(mandate_ids),
                context=context)}

    def generate_retrocessions(self, cr, uid, ids, context=None):
        """
        =======================
        generate_retrocessions
        =======================
        Generate retrocessions for valid selected mandates
        """
        wizard = self.browse(cr, uid, ids, context=context)[0]
        mandate_key = MANDATE_M2O.get(wizard.model, False)
        mandate_ids = self.mandate_selection_analysis(
            cr,
            uid,
            wizard.month,
            wizard.year,
            wizard.model,
            eval(
                wizard.mandate_ids),
            mode='ids',
            context=context)

        monthly_mandate_ids = [
            mandate['id'] for mandate in self.pool.get(
                wizard.model).read(
                cr,
                uid,
                mandate_ids,
                ['retrocession_mode']) if
            mandate['retrocession_mode'] == 'month']
        yearly_mandate_ids = list(set(mandate_ids) - set(monthly_mandate_ids))

        worker_pivot = int(
            self.pool.get('ir.config_parameter').get_param(
                cr,
                uid,
                'worker_pivot',
                10))

        vals = dict(month=wizard.month,
                    year=wizard.year)

        session = ConnectorSession(cr, uid, context=context)
        if len(monthly_mandate_ids) > worker_pivot:
            create_retrocessions.delay(
                session,
                self._name,
                monthly_mandate_ids,
                vals,
                mandate_key,
                context)
        else:
            create_retrocessions(
                session,
                self._name,
                monthly_mandate_ids,
                vals,
                mandate_key,
                context)

        vals.pop('month')

        if len(yearly_mandate_ids) > worker_pivot:
            create_retrocessions.delay(
                session,
                self._name,
                yearly_mandate_ids,
                vals,
                mandate_key,
                context)
        else:
            create_retrocessions(
                session,
                self._name,
                yearly_mandate_ids,
                vals,
                mandate_key,
                context)


@job
def create_retrocessions(
        session,
        model_name,
        ids,
        vals,
        mandate_key,
        context=None):
    """
    =======================
    create_retrocessions
    =======================
    Create retrocessions for given mandates
    """
    for mandate_id in ids:
        vals[mandate_key] = mandate_id
        session.pool['retrocession'].create(
            session.cr,
            session.uid,
            vals,
            context=context)
