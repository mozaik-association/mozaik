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


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def write(self, cr, uid, ids, vals, context=None, check=True,
              update_check=True):
        """
        Change state of retrocession during reconciliation process
        """
        res = super(
            account_move_line,
            self).write(
            cr,
            uid,
            ids,
            vals,
            context=context,
            check=check,
            update_check=check)
        reconcile_id = vals.get('reconcile_id', False)
        if reconcile_id:
            retro_obj = self.pool['retrocession']
            move_lines = self.search_read(
                cr, uid, [
                    ('reconcile_id', '=', reconcile_id)], ['move_id'],
                context=context)
            move_ids = [line['move_id'][0] for line in move_lines]
            if len(move_ids) > 1:
                retro_ids = retro_obj.search(
                    cr, uid, [
                        ('move_id', 'in', move_ids)], context=context)
                if retro_ids:
                    retro_obj.action_done(cr, uid, retro_ids, context=context)
        return res
