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
import base64
from cStringIO import StringIO
import datetime

import xlwt

from openerp.osv import orm, fields
from openerp.tools.translate import _


AVAILABLE_REPORTS = [
    ('fractionations', 'Fractionations'),
    ('certificates', 'Payment Certificates'),
]

FRACTIONATION_REPORTS_MANDATES_HEADER = [
    _('Mandate Category'),
    _('Assembly'),
    _('Start Date'),
    _('End Date'),
    _('Representative'),
    _('Retrocession Mode'),
    _('Amount Due'),
    _('Amount Paid'),
]

FRACTIONATION_REPORTS_INSTANCE_HEADER = [
    _('Power Level'),
    _('Instance'),
    _('Amount'),
]


class report_retrocession_wizard(orm.TransientModel):
    _name = "report.retrocession.wizard"
    _description = 'Retrocessions Reports Generator'

    _columns = {
        'model': fields.char('Model', size=128, required=True),
        'report': fields.selection(AVAILABLE_REPORTS,
                                   'Report',
                                   required=True,),
        'mandate_ids': fields.text('IDS', required=True),
        'year': fields.char('Year', size=128, required=True),
        'mandate_selected': fields.integer('Selected Mandates'),
        'yearly_count': fields.integer('Yearly Retrocessions Selected'),
        'monthly_count': fields.integer('Monthly Retrocessions Selected'),
        'yearly_print': fields.integer('Yearly Retrocessions To Print'),
        'monthly_print': fields.integer('Monthly Retrocessions To Print'),
        'total_mandates': fields.integer('Mandates To Print'),
        'data': fields.binary('XLS', readonly=True),
        'export_filename': fields.char('Export XLS Filename', size=128),
    }

    def default_get(self, cr, uid, flds, context=None):
        """
        To get default values for the object.
        """
        context = context or {}
        ids = []
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
            'year': datetime.date.today().strftime("%Y"),
            'mandate_selected': len(ids),
            'report': context.get('document', 'certificates'),
        }

        return res

    def mandate_selection_analysis(self, cr, uid, year, model, ids,
                                   mode='onchange', context=None):
        """
        ===============
        mandate_selection_analysis
        ==============)
        Analyse mandate selection and give an overview of expected results
        """
        monthly_ids = self.pool[model].search(
            cr, uid, [
                ('retrocession_mode', '=', 'month'),
                ('id', 'in', ids),
                ('active', '<=', True), ])
        yearly_ids = self.pool[model].search(
            cr, uid, [
                ('retrocession_mode', '=', 'year'),
                ('id', 'in', ids),
                ('active', '<=', True), ])

        retro_pool = self.pool['retrocession']
        foreign_key = retro_pool.get_relation_column_name(cr,
                                                          uid,
                                                          model,
                                                          context=context)

        monthly_print_ids = [data[foreign_key][0] for data in
                             retro_pool.search_read(cr, uid, [
                                 ('year', '=', year),
                                 (foreign_key, 'in', monthly_ids),
                                 ('state', 'in',
                                  ['validated', 'done']),
                                 ('active', '<=', True),
                                 ('amount_paid', '>', 0)],
            fields=[foreign_key],
            context=context)]

        yearly_print_ids = [data[foreign_key][0] for data in
                            retro_pool.search_read(cr, uid, [
                                ('year', '=', year),
                                (foreign_key, 'in', yearly_ids),
                                ('state', 'in',
                                 ['validated', 'done']),
                                ('active', '<=', True),
                                ('amount_paid', '>', 0)],
            fields=[foreign_key],
            context=context)]

        if mode == 'ids':
            res = monthly_print_ids + yearly_print_ids
        else:
            total = len(yearly_print_ids) + len(monthly_print_ids)
            res = {
                'total_mandates': total,
                'yearly_count': len(yearly_ids),
                'yearly_print': len(yearly_print_ids),
                'monthly_count': len(monthly_ids),
                'monthly_print': len(monthly_print_ids),
            }

        return res

    def onchange_year(self, cr, uid, ids, year, model, mandate_ids,
                      context=None):
        return {
            'value': self.mandate_selection_analysis(cr, uid, year, model,
                                                     eval(mandate_ids),
                                                     context=context)
        }

    def print_report(self, cr, uid, ids, context=None):
        """
        =======================
        print_report
        =======================
        Print report for valid selected mandates
        """
        wizard = self.browse(cr, uid, ids, context=context)[0]
        if wizard.report == 'certificates':
            return self.print_certificates(cr, uid, wizard, context=context)
        elif wizard.report == 'fractionations':
            return self.print_fractionations(cr, uid, wizard, context=context)

    def _get_mandate_retrocession_amounts(self, cr, uid, mandate_model,
                                          mandate_id, year, context=None):
        """
        =================================
        _get_mandate_retrocession_amounts
        =================================
        Return amount_to_pay and amount_paid total
        for all retrocession of a given mandate for a specific year
        """
        retro_pool = self.pool.get('retrocession')
        foreign_key = retro_pool.get_relation_column_name(cr,
                                                          uid,
                                                          mandate_model,
                                                          context=context)
        data = retro_pool.search_read(
            cr,
            uid,
            [(foreign_key, '=', mandate_id),
             ('year', '=', year),
             ('state', 'in', ['validated', 'done']),
             ('active', '<=', True)],
            ['amount_total', 'amount_paid'],
            context=context)
        amount_total = sum([record['amount_total'] for record in data])
        amount_paid = sum([record['amount_paid'] for record in data])
        return amount_total, amount_paid

    def _get_fractionation_data(self, cr, uid, mandate_ids, mandate_model,
                                assembly_model, year, context=None):
        """
        =======================
        _get_fractionation_data
        =======================
        Return mandate data and instance data (aggregation) needed to generate
        Excel sheets
        """
        assembly_key = self.pool[mandate_model].get_relation_column_name(
            cr,
            uid,
            assembly_model,
            context=context)
        mandates_data = {}
        instances_data = {}
        for mandate in self.pool[mandate_model].browse(cr,
                                                       uid,
                                                       mandate_ids,
                                                       context=context):

            fractionation = mandate[assembly_key].fractionation_id \
                or mandate.mandate_category_id.fractionation_id
            if not fractionation:

                continue

            level_dict = {}
            for line in fractionation.fractionation_line_ids:
                level_dict[line.power_level_id.id] = line.percentage

            instance_id = mandate.partner_id.int_instance_id.id

            amount_total, amount_paid = self._get_mandate_retrocession_amounts(
                cr,
                uid,
                mandate_model,
                mandate.id,
                year,
                context=context)
            inst_split, pl_split = self._split_amount(cr,
                                                      uid,
                                                      amount_paid,
                                                      level_dict,
                                                      instance_id,
                                                      context=context)
            for instance_id in inst_split:
                data = inst_split[instance_id]
                if not instances_data.get(instance_id, False):
                    instances_data[instance_id] = data
                else:
                    instances_data[instance_id]['Amount'] += data['Amount']

            data = {}
            data['Mandate Category'] = mandate.mandate_category_id.name
            data['Assembly'] = mandate[assembly_key].name
            data['Start Date'] = self.pool['res.lang'].format_date(
                cr,
                uid,
                mandate.start_date,
                context=context)
            data['End Date'] = self.pool['res.lang'].format_date(
                cr,
                uid,
                mandate.end_date or mandate.deadline_date,
                context=context)
            data['Representative'] = mandate.partner_id.name
            data['Retrocession Mode'] = mandate.retrocession_mode
            data['Amount Due'] = amount_total
            data['Amount Paid'] = amount_paid
            data['split'] = pl_split
            mandates_data[mandate.id] = data

        return instances_data, mandates_data

    def _split_amount(self, cr, uid, amount, rules, instance_id, context=None):
        """
        ============================
        _split_amount_by_power_level
        ============================
        Return amount splitted by power level
        """
        inst_split, pl_split = {}, {}
        rest = amount
        while True:
            instance = self.pool['int.instance'].browse(cr,
                                                        uid,
                                                        instance_id,
                                                        context=context)

            power_level_id = instance.power_level_id.id
            power_level_name = instance.power_level_id.name
            if power_level_id in rules:
                percentage = rules[power_level_id]
                split_value = round((amount * percentage) / 100, 2)
                rest -= split_value
                pl_split[power_level_id] = dict(id=instance.id,
                                                name=instance.name,
                                                amount=split_value)
                inst_split[instance_id] = {'Instance': instance.name,
                                           'Amount': split_value,
                                           'Power Level': power_level_name}

            if not instance.parent_id:
                break
            else:
                instance_id = instance.parent_id.id

        if rest > 0:
            pl_split['Unfractioned'] = rest
            inst_split['Unfractioned'] = {'Instance': 'Unfractioned Amount',
                                          'Amount': rest,
                                          'Power Level': ''}

        return inst_split, pl_split

    def _extract_power_level_ids(self, cr, uid, mandates_data, context=None):
        """
        =========================
        _extract_power_level_ids
        =========================
        Return list of power level ids needed for report header
        """
        ids = []
        for mandate_key in mandates_data:
            ids.extend([key for key in mandates_data[mandate_key]['split']
                        if key != 'Unfractioned'])

        return list(set(ids))

    def print_certificates(self, cr, uid, wizard, context=None):
        """
        =======================
        print_certificates
        =======================
        Print certificates for valid selected mandates
        """
        mandate_ids = self.mandate_selection_analysis(
            cr,
            uid,
            wizard.year,
            wizard.model,
            eval(wizard.mandate_ids),
            mode='ids', context=context)
        context['active_ids'] = mandate_ids
        secretariat_dict = {}
        need_signature = {}
        retro_amounts = {}
        for mandate in self.pool[wizard.model].read(
                cr,
                uid,
                mandate_ids,
                ['retro_instance_id'],
                context=context):
            instance_id = mandate['retro_instance_id'][0]
            default_instance_id = self.pool.get('int.instance').get_default(
                cr,
                uid,
                context=context)
            need_signature[mandate['id']] = instance_id == default_instance_id
            int_ass_pool = self.pool['int.assembly']
            assembly_ids = int_ass_pool.search(
                cr, uid, [
                    ('instance_id', '=', instance_id),
                    ('is_secretariat', '=', True)],
                context=context)
            if not assembly_ids:
                secretariat_name = False
            else:
                secretariat_name = int_ass_pool.read(cr,
                                                     uid,
                                                     assembly_ids[0],
                                                     ['name'],
                                                     context=context)['name']

            secretariat_dict[mandate['id']] = secretariat_name

            amount_total, amount_paid = self._get_mandate_retrocession_amounts(
                cr,
                uid,
                wizard.model,
                mandate['id'],
                wizard.year,
                context=context)
            retro_amounts[mandate['id']] = amount_paid \
                if amount_paid <= amount_total else amount_total

        data = {'model': wizard.model,
                'year': wizard.year,
                'secretariat': secretariat_dict,
                'signature': need_signature,
                'amounts': retro_amounts,
                }
        return self.pool['report'].get_action(
            cr,
            uid,
            [],
            'mozaik_retrocession.report_payment_certificate',
            data=data,
            context=context)

    def print_fractionations(self, cr, uid, wizard, context=None):
        """
        =======================
        print_fractionations
        =======================
        Generate xls file about fractionations for valid selected mandates
        """
        if wizard.model == 'sta.mandate':
            assembly_model = 'sta.assembly'
        else:
            assembly_model = 'ext.assembly'

        mandate_ids = self.mandate_selection_analysis(
            cr,
            uid,
            wizard.year,
            wizard.model,
            eval(wizard.mandate_ids),
            mode='ids', context=context)
        context['active_ids'] = mandate_ids

        inst_data, mandates_data = self._get_fractionation_data(
            cr,
            uid,
            mandate_ids,
            wizard.model,
            assembly_model,
            wizard.year,
            context=context)

        power_level_ids = self._extract_power_level_ids(cr,
                                                        uid,
                                                        mandates_data,
                                                        context=context)
        xls_wbk = xlwt.Workbook()
        xls_sheet = xls_wbk.add_sheet(_('Mandates'))

        style_string = "font: bold on; border: top thin, right thin,\
                        bottom thin, left thin;align: horiz center"
        headerstyle = xlwt.easyxf(style_string)

        report_header = FRACTIONATION_REPORTS_MANDATES_HEADER[:]

        pl_start_index = len(report_header)
        pl_index = {}
        index = 0
        for power_level in self.pool['int.power.level'].read(cr,
                                                             uid,
                                                             power_level_ids,
                                                             ['name'],
                                                             context=context):
            report_header.append(power_level['name'])
            pl_index[power_level['id']] = pl_start_index + index
            index += 2

        report_header.append('Unfractioned')
        pl_index['Unfractioned'] = pl_start_index + index

        step = 0
        for icol, column in enumerate(report_header):
            if icol < pl_start_index or column == 'Unfractioned':
                icol += step
                xls_sheet.write(0, icol, column, headerstyle)
            else:
                # power level data need 2 columns
                icol += step
                next_col = icol + 1
                xls_sheet.write_merge(0, 0, icol, next_col,
                                      column, headerstyle)
                step += 1

        xls_sheet.set_panes_frozen(True)
        xls_sheet.set_horz_split_pos(1)
        xls_sheet.set_remove_splits(True)

        step = 0
        for idata, key in enumerate(mandates_data):
            data = mandates_data[key]
            irow = idata + 1
            for icol, column in enumerate(report_header):
                if icol < pl_start_index:
                    xls_sheet.write(irow, icol, data.get(column, ''))
                else:
                    break
            # write power level data
            for pl_id in data['split']:
                icol = pl_index[pl_id]
                value = data['split'][pl_id]
                if pl_id != 'Unfractioned':
                    xls_sheet.write(irow, icol, value.get('name', ''))
                    icol += 1
                    xls_sheet.write(irow, icol, value.get('amount', ''))
                else:
                    xls_sheet.write(irow, icol, value)

        xls_sheet = xls_wbk.add_sheet(_('Instances'))
        report_header = FRACTIONATION_REPORTS_INSTANCE_HEADER[:]
        for icol, column in enumerate(report_header):
            xls_sheet.write(0, icol, column, headerstyle)

        xls_sheet.set_panes_frozen(True)
        xls_sheet.set_horz_split_pos(1)
        xls_sheet.set_remove_splits(True)

        irow = 1
        for instance_id in inst_data:
            data = inst_data[instance_id]
            for icol, column in enumerate(report_header):
                xls_sheet.write(irow, icol, data[column])
            irow += 1

        file_data = StringIO()
        xls_wbk.save(file_data)

        out = base64.encodestring(file_data.getvalue())

        filename = _("Fractionations") + '_' + wizard.year + '.xls'
        self.write(cr, uid, wizard.id,
                   {'data': out,
                    'export_filename': filename},
                   context=context)

        return {
            'name': 'Fractionations Report',
            'type': 'ir.actions.act_window',
            'res_model': 'report.retrocession.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wizard.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
