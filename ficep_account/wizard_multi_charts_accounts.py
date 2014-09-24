# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Acsone SA/NV
#    Copyright (c) 2013 Acsone SA/NV (http://www.acsone.eu)
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

from openerp.osv import orm
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class wizard_multi_charts_accounts(orm.TransientModel):
    """
    Execute wizard automatically without showing the wizard popup window
    """
    _inherit = 'wizard.multi.charts.accounts'

    def generate_properties(self, cr, uid, chart_template_id, acc_template_ref, company_id, context=None):
        super(wizard_multi_charts_accounts, self).generate_properties(cr, uid, chart_template_id, acc_template_ref, company_id, context=context)

        property_obj = self.pool.get('ir.property')
        field_obj = self.pool.get('ir.model.fields')
        todo_list = [
            ('property_retrocession_account', 'mandate.category', 'account.account'),
            ('property_retrocession_cost_account', 'mandate.category', 'account.account'),
            ('property_subscription_account', 'product.template', 'account.account')
        ]
        template = self.pool.get('account.chart.template').browse(cr, uid, chart_template_id, context=context)
        for record in todo_list:
            account = getattr(template, record[0])
            value = account and 'account.account,' + str(acc_template_ref[account.id]) or False
            if value:
                field = field_obj.search(cr, uid, [('name', '=', record[0]), ('model', '=', record[1]), ('relation', '=', record[2])], context=context)
                vals = {
                    'name': record[0],
                    'company_id': company_id,
                    'fields_id': field[0],
                    'value': value,
                }
                property_ids = property_obj.search(cr, uid, [('name', '=', record[0]), ('company_id', '=', company_id)], context=context)
                if property_ids:
                    #the property exist: modify it
                    property_obj.write(cr, uid, property_ids, vals, context=context)
                else:
                    #create the property
                    property_obj.create(cr, uid, vals, context=context)
        self._prepare_operation_templates(cr, uid, template, acc_template_ref,
                                           context=context)
        return True

    def _prepare_operation_templates(self, cr, uid, template, acc_template_ref,
                                     context=None):
        account = getattr(template, 'property_subscription_account')
        vals = {'name': _('Subscriptions'),
                'account_id': acc_template_ref[account.id],
                'label':  _('Subscriptions'),
                'amount_type': 'percentage_of_total',
                'amount': 100.0
                }
        self.pool.get('account.statement.operation.template').create(
                                                             cr,
                                                             uid,
                                                             vals,
                                                             context=context)

    def _prepare_all_journals(self, cr, uid, chart_template_id, acc_template_ref, company_id, context=None):
        journal_data = super(wizard_multi_charts_accounts, self)._prepare_all_journals(cr, uid, chart_template_id, acc_template_ref, company_id, context=context)

        template = self.pool.get('account.chart.template').browse(cr, uid, chart_template_id, context=context)
        default_debit_account = acc_template_ref.get(template.property_account_receivable.id)
        default_credit_account = self.pool.get('account.account').search(cr, uid, [('code', '=', '749200'), ('company_id', '=', company_id)], context=context, limit=1)[0]

        vals = {
                'type': 'sale',
                'name': 'RETROCESSIONS',
                'code': 'RETRO',
                'company_id': company_id,
                'default_credit_account_id': default_credit_account,
                'default_debit_account_id': default_debit_account,
                'update_posted': True,
                }

        seq = {
            'name': vals['name'],
            'implementation': 'no_gap',
            'prefix': vals['code'].upper() + "/%(year)s/",
            'padding': 6,
            'number_increment': 1
        }

        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']

        sequence_id = self.pool.get('ir.sequence').create(cr, uid, seq)

        vals.update({'sequence_id': sequence_id})

        journal_data.append(vals)

        return journal_data
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
