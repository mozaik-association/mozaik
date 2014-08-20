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


class report_payment_certificate_wizard(orm.TransientModel):
    _name = "report.payment.certificate.wizard"
    _description = 'Payment certificate Generator'

    _columns = {
        'model': fields.char('Model', size=128, required=True),
        'mandate_ids': fields.text('IDS', required=True),
        'year': fields.char('Year', size=128, required=True),
        'mandate_selected': fields.integer('Selected Mandates'),
        'yearly_count': fields.integer('Yearly Retrocessions Selected'),
        'monthly_count': fields.integer('Monthly Retrocessions Selected'),
        'yearly_print': fields.integer('Yearly Retrocessions To Print'),
        'monthly_print': fields.integer('Monthly Retrocessions To Print'),
        'total_certificate': fields.integer('Certificates To Produce'),
    }

    def default_get(self, cr, uid, flds, context=None):
        """
        To get default values for the object.
        """
        context = context or {}
        ids = context.get('active_ids') or (context.get('active_id')\
                                        and [context.get('active_id')]) or []

        res = {
            'model': context.get('active_model', False),
            'mandate_ids': str(ids),
            'year': datetime.date.today().strftime("%Y"),
            'mandate_selected': len(ids),
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
        monthly_ids = self.pool[model].search(cr, uid,\
                                          [('retrocession_mode', '=', 'month'),
                                           ('id', 'in', ids),
                                           ('active', '<=', True),
                                          ])
        yearly_ids = self.pool[model].search(cr, uid,\
                                          [('retrocession_mode', '=', 'year'),
                                           ('id', 'in', ids),
                                           ('active', '<=', True),
                                          ])

        retro_pool = self.pool['retrocession']
        foreign_key = retro_pool.get_relation_column_name(cr,
                                                          uid,
                                                          model,
                                                          context=context)

        monthly_print_ids = [data[foreign_key][0] for data in
                                             retro_pool.search_read(cr, uid, [
                                             ('year', '=', year),
                                             (foreign_key, 'in', monthly_ids),
                                             ('state', '=', 'done'),
                                             ('active', '=', False),
                                             ('amount_paid', '>', 0)],
                                             fields=[foreign_key],
                                             context=context)]

        yearly_print_ids = [data[foreign_key][0] for data in
                                             retro_pool.search_read(cr, uid, [
                                             ('year', '=', year),
                                             (foreign_key, 'in', yearly_ids),
                                             ('state', '=', 'done'),
                                             ('active', '=', False),
                                             ('amount_paid', '>', 0)],
                                             fields=[foreign_key],
                                             context=context)]

        if mode == 'ids':
            res = monthly_print_ids + yearly_print_ids
        else:
            total = len(yearly_print_ids) + len(monthly_print_ids)
            res = {
                'total_certificate': total,
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

    def print_certificates(self, cr, uid, ids, context=None):
        """
        =======================
        print_certificates
        =======================
        Print certificates for valid selected mandates
        """
        wizard = self.browse(cr, uid, ids, context=context)[0]

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
            assembly_ids = int_ass_pool.search(cr, uid,
                                        [('instance_id', '=', instance_id),
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

            retro_pool = self.pool.get('retrocession')
            foreign_key = retro_pool.get_relation_column_name(cr,
                                                              uid,
                                                              wizard.model,
                                                              context=context)
            data = retro_pool.search_read(
                                         cr,
                                         uid,
                                         [(foreign_key, '=', mandate['id']),
                                          ('state', '=', 'done'),
                                          ('active', '=', False),
                                          ('amount_paid', '>', 0)],
                                         ['amount_paid'],
                                         context=context)
            amount_paid = sum([record['amount_paid'] for record in data])
            retro_amounts[mandate['id']] = amount_paid

        data = {'model': wizard.model,
                'year': wizard.year,
                'secretariat': secretariat_dict,
                'signature': need_signature,
                'amounts': retro_amounts,
                }
        return self.pool['report'].get_action(cr, uid, [],
                        'ficep_retrocession.report_payment_certificate',
                         data=data,
                         context=context)
