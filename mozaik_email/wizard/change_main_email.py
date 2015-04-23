# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_email, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_email is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_email is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_email.
#     If not, see <http://www.gnu.org/licenses/>.
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
        context = dict(context)
        res = super(change_main_email, self).default_get(
            cr, uid, flds, context=context)
        if context.get('mode', False) == 'switch':
            coord = self.pool[context.get('target_model')].browse(
                cr, uid, context.get('target_id', False))
            res['email'] = coord.email
        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []
        if len(ids) == 1:
            partner = self.pool['res.partner'].browse(
                cr, SUPERUSER_ID, ids[0], context=context)
            res['old_email'] = partner.email_coordinate_id.email
        return res
