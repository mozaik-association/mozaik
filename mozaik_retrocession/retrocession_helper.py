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
from openerp.osv import orm


class RetrocessionHelper(orm.Model):
    _name = 'retrocession.helper'
    _auto = False

    def create_fiscal_year(self, cr, uid, year, context=None):
        company_id = self.pool['ir.model.data'].xmlid_to_res_id(
            cr, uid, 'base.main_company')
        fiscalyear_obj = self.pool['account.fiscalyear']
        dm = [('company_id', '=', company_id), ('code', '=', year)]
        if fiscalyear_obj.search(cr, uid, dm):
            return
        fiscalyear_id = fiscalyear_obj.create(cr, uid, {
            'name': year,
            'code': year,
            'date_start': year + '-01-01',
            'date_stop': year + '-12-31',
            'company_id': company_id
        })
        fiscalyear_obj.create_period3(cr, uid, [fiscalyear_id])

    def validate_retrocession_with_accounting(self, cr, uid, retro_ids,
                                              context=None):

        retro_ids = isinstance(retro_ids, (long, int))\
            and [retro_ids] or retro_ids

        registry = self.pool
        rule_pool = registry['calculation.rule']
        retro_pool = registry['retrocession']
        abs_pool = registry['account.bank.statement']
        absl_pool = registry['account.bank.statement.line']

        for retro_id in retro_ids:

            retro_data = retro_pool.read(cr,
                                         uid,
                                         retro_id,
                                         ['state', 'need_account_management'],
                                         context=context)

            if retro_data['state'] == 'done'\
               or not retro_data['need_account_management']:
                continue

            rule_ids = rule_pool.search(cr, uid,
                                        [('retrocession_id', '=', retro_id),
                                         ('is_deductible', '=', False)],
                                        context=context)
            if not rule_ids:
                continue

            rule_pool.write(cr, uid, rule_ids[0], {'amount': 45000.00})

            retro_pool.action_validate(cr, uid, [retro_id])
            retro = retro_pool.browse(cr, uid, retro_id, context=context)

            statement_vals = {'name': ('/%s' % retro.unique_id)}

            b_statement_id = abs_pool.create(cr,
                                             uid,
                                             statement_vals,
                                             context={'journal_type': 'bank'})

            statement_line_vals = {'statement_id': b_statement_id,
                                   'name': retro.sta_mandate_id.reference
                                   if retro.sta_mandate_id else
                                   retro.ext_mandate_id.reference,
                                   'amount': retro.amount_due,
                                   'partner_id': retro.partner_id.id,
                                   'ref': retro.unique_id
                                   }
            line_id = absl_pool.create(cr,
                                       uid,
                                       statement_line_vals,
                                       context=context)
            line = absl_pool.browse(cr, uid, line_id, context=context)

            ret = absl_pool.get_reconciliation_proposition(cr,
                                                           uid,
                                                           line,
                                                           context=context)
            vals = {'counterpart_move_line_id': ret[0]['id'],
                    'debit': ret[0]['credit'],
                    'credit': ret[0]['debit'],
                    }

            absl_pool.process_reconciliation(cr,
                                             uid,
                                             line_id,
                                             [vals],
                                             context=context)
        return True
