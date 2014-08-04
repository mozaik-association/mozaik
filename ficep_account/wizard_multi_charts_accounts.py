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

    def _prepare_all_journals(self, cr, uid, chart_template_id, acc_template_ref, company_id, context=None):
        journal_data = super(wizard_multi_charts_accounts, self)._prepare_all_journals(cr, uid, chart_template_id, acc_template_ref, company_id, context=context)

        template = self.pool.get('account.chart.template').browse(cr, uid, chart_template_id, context=context)
        default_debit_account = acc_template_ref.get(template.property_account_receivable.id)

        default_credit_account_ids = self.pool.get('account.account').search(cr, uid, [('code', '=', '749300'), ('company_id', '=', company_id)], context=context, limit=1)
        default_credit_account_id = default_credit_account_ids and \
                    default_credit_account_ids[0] or False
        if not default_credit_account_id:
            _logger.warning(_('WARNING'), _('No credit account found'))

        vals = {
                'type': 'sale',
                'name': 'SUBSCRIPTIONS',
                'code': 'SUB',
                'company_id': company_id,
                'default_credit_account_id': default_credit_account_id,
                'default_debit_account_id': default_debit_account,
                'update_posted': True,
                }
        journal_data.append(vals)

        return journal_data

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
