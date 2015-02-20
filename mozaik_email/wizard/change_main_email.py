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


class change_main_email(orm.TransientModel):

    _name = 'change.main.email'
    _inherit = 'change.main.coordinate'
    _description = 'Change Main Email Wizard'

    _columns = {
        'old_email': fields.char('Current Main Email'),
        'email': fields.char('New Main Email', required=True),
    }

    def default_get(self, cr, uid, flds, context):
        res = super(change_main_email, self).default_get(cr, uid, flds, context=context)
        if context.get('mode', False) == 'switch':
            coord = self.pool.get(context.get('target_model')).browse(cr, uid, context.get('target_id', False))
            res['email'] = coord.email
        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []
        if len(ids) == 1:
            partner = self.pool.get('res.partner').browse(cr, SUPERUSER_ID, ids[0], context=context)
            res['old_email'] = partner.email_coordinate_id.email
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
