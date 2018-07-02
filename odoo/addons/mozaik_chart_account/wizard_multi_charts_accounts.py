# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_account, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_account is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_account is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_account.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
import logging
_logger = logging.getLogger(__name__)


class wizard_multi_charts_accounts(orm.TransientModel):

    """
    Execute wizard automatically without showing the wizard popup window
    """
    _inherit = 'wizard.multi.charts.accounts'

    def _prepare_all_journals(self, cr, uid, chart_template_id,
                              acc_template_ref, company_id, context=None):
        journal_data = super(
            wizard_multi_charts_accounts, self)._prepare_all_journals(
                cr, uid, chart_template_id, acc_template_ref, company_id,
                context=context)

        template = self.pool.get('account.chart.template').browse(
            cr, uid, chart_template_id, context=context)
        default_debit_account = acc_template_ref.get(
            template.property_account_receivable.id)
        default_credit_account_ids = self.pool.get('account.account').search(
            cr, uid, [('code', '=', '749200'),
                      ('company_id', '=', company_id)],
            context=context, limit=1)
        default_credit_account_id = default_credit_account_ids and \
            default_credit_account_ids[0] or False
        vals = {
            'type': 'sale',
            'name': 'RETROCESSIONS',
            'code': 'RETRO',
            'company_id': company_id,
            'default_credit_account_id': default_credit_account_id,
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
