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

FAILURE_AVAILABLE_TYPES = [
    ('f1', 'No longer lives at the mentioned address'),
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
            value = self.pool['ir.translation']._get_source(cr, uid, name, 'selection', context['lang'], src)
        if not value:
            value = src
        res = {'description': value}
        return {
            'value': res
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
