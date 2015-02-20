# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class email_template(orm.Model):

    _inherit = "email.template"

    _columns = {
        'res_users_ids': fields.many2many(
            'res.users', 'email_template_res_users_rel',
            id1='template_id', id2='user_id',
            string='Owners', required=True),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance', select=True),
    }

    _defaults = {
        'model_id': lambda self, cr, uid, c: self.pool['ir.model'].search(
            cr, uid, [('model', '=', 'email.coordinate')])[0],
        'res_users_ids': lambda self, cr, uid, c: [uid],
    }
