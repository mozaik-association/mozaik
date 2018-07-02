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

from openerp.osv import orm, fields


class account_chart_template(orm.Model):
    _inherit = "account.chart.template"

    _columns = {
        'property_retrocession_account': fields.many2one(
            'account.account.template', 'Retrocession Account'),
        'property_retrocession_cost_account': fields.many2one(
            'account.account.template', 'Retrocession Cost Account'),
        'property_subscription_account': fields.many2one(
            'account.account.template', 'Subscription Account'),
    }


class account_account(orm.Model):

    _inherit = 'account.account'

    def _check_coa_loaded(self, cr, uid, company_id, coa_id, context=None):
        """
        Determine if a COA is already loaded for a specific company
        """
        template = self.pool['account.chart.template'].browse(
            cr, uid, coa_id, context=context)
        dom = [('chart_template_id', '=', coa_id)]
        if template.account_root_id.id:
            dom = ['|'] + dom + [
                '&',
                ('parent_id', 'child_of', [template.account_root_id.id]),
                ('chart_template_id', '=', False)
            ]
        codes = self.pool['account.account.template'].search_read(
            cr, uid, [('nocreate', '!=', True)] + dom,
            ['code'], context=context)

        codes = [c['code'] for c in codes]

        account_id = self.search(
            cr, uid,
            [('company_id', '=', company_id), ('code', 'in', codes)],
            limit=1, context=context)
        return account_id
