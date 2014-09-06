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


class account_chart_template(orm.Model):
    _inherit = "account.chart.template"

    _columns = {
        'property_retrocession_account': fields.many2one('account.account.template', 'Retrocessions Account'),
        'property_retrocession_cost_account': fields.many2one('account.account.template', 'Retrocessions Cost Account'),
    }


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        """
        Change state of retrocession during reconciliation process
        """
        res = super(account_move_line, self).write(cr, uid, ids, vals, context=context, check=check, update_check=check)
        reconcile_id = vals.get('reconcile_id', False)
        if reconcile_id:
            retro_obj = self.pool['retrocession']
            move_lines = self.search_read(cr, uid, [('reconcile_id', '=', reconcile_id)],
                                                   ['move_id'], context=context)
            move_ids = [line['move_id'][0] for line in move_lines]
            if len(move_ids) > 1:
                retro_ids = retro_obj.search(cr, uid, [('move_id', 'in', move_ids)], context=context)
                if retro_ids:
                    retro_obj.action_done(cr, uid, retro_ids, context=context)
        return res
