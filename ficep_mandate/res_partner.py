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
from openerp.tools import SUPERUSER_ID


class res_partner(orm.Model):

    _name = 'res.partner'
    _inherit = ['res.partner']

    _columns = {
        'sta_mandate_ids': fields.one2many('sta.mandate', 'partner_id', 'State Mandates', domain=[('active', '=', True)]),
        'sta_mandate_inactive_ids': fields.one2many('sta.mandate', 'partner_id', 'State Mandates', domain=[('active', '=', False)]),
        'sta_candidature_ids': fields.one2many('sta.candidature', 'partner_id', 'State Candidatures', domain=[('active', '=', True)]),
        'sta_candidature_inactive_ids': fields.one2many('sta.candidature', 'partner_id', 'State Candidatures', domain=[('active', '=', False)]),
    }

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        """
        default = default or {}
        default.update({
            'sta_mandate_ids': [],
            'sta_mandate_inactive_ids': [],
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        When invalidating a partner, invalidates also its mandates and candidatures
        """
        if 'active' in vals and not vals['active']:
            mandate_obj = self.pool['sta.mandate']
            mandate_ids = mandate_obj.search(cr, SUPERUSER_ID, [('partner_id', 'in', ids)], context=context)
            if mandate_ids:
                mandate_obj.action_invalidate(cr, SUPERUSER_ID, mandate_ids, context=context)

            candidature_obj = self.pool['sta.candidature']
            candidature_ids = candidature_obj.search(cr, SUPERUSER_ID, [('partner_id', 'in', ids)], context=context)
            if candidature_ids:
                candidature_obj.action_invalidate(cr, SUPERUSER_ID, candidature_ids, context=context)

        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
