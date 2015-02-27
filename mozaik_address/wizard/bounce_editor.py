# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_address, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_address is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_address is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_address.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields

FAILURE_AVAILABLE_TYPES = [
    ('nomail', 'No longer receives mail at the mentioned address'),
    ('moved', 'Moved'),
    ('bad', 'Incomplete/Invalid address'),
    ('unknown', 'Unknown'),
    ('refused', 'Refused'),
    ('deceased', 'Deceased'),
    ('unclaimed', 'Unclaimed'),
    ('improper', 'Improper box number'),
]


class bounce_editor(orm.TransientModel):

    _inherit = 'bounce.editor'

    _columns = {
        'reason': fields.selection(FAILURE_AVAILABLE_TYPES, 'Reason'),
    }

    _defaults = {
        'reason': False,
    }

# view methods: onchange, button

    def onchange_reason(self, cr, uid, ids, reason, context=None):
        if not reason:
            return {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        src = [x[1] for x in FAILURE_AVAILABLE_TYPES if x[0] == reason][0]
        value = False
        if context.get('lang'):
            name = '%s,reason' % self._inherit
            value = self.pool['ir.translation']._get_source(
                cr, uid, name, 'selection', context['lang'], src)
        if not value:
            value = src
        res = {'description': value}
        return {
            'value': res,
        }
