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

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields


class res_partner(orm.Model):

    _inherit = "res.partner"

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

    def _get_main_email_coordinate_ids(self, cr, uid, ids, name, args, context=None):
        """
        ==============================
        _get_main_email_coordinate_ids
        ==============================
        Reset *_coordinate_id fields with corresponding main email coordinate ids
        :param ids: partner ids for which new *_coordinate_id fields have to be recomputed
        :type name: char
        :rparam: dictionary for all partner id with requested main coordinate ids
        :rtype: dict {partner_id:{'email_coordinate_id': main_email_id,}}
        Note:
        Calling and result convention: Single mode
        """
        result = {i: False for i in ids}
        coord_obj = self.pool['email.coordinate']
        coordinate_ids = coord_obj.search(cr, uid, [('partner_id', 'in', ids),
                                                    ('is_main', '=', True),
                                                    ('active', '<=', True)], context=context)
        for coord in coord_obj.browse(
            cr, SUPERUSER_ID, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                result[coord.partner_id.id] = coord.id
        return result

    def _get_main_email(self, cr, uid, ids, name, args, context=None):
        """
        ===============
        _get_main_email
        ===============
        Reset main email field
        :param ids: partner ids for which the email has to be recomputed
        :type name: char
        :rparam: dictionary for all partner ids with the requested main email number
        :rtype: dict {partner_id: main_email}
        Note:
        Calling and result convention: Single mode
        """
        result = {i: False for i in ids}
        coord_obj = self.pool['email.coordinate']
        coordinate_ids = coord_obj.search(cr, SUPERUSER_ID, [('partner_id', 'in', ids),
                                                             ('is_main', '=', True),
                                                             ('active', '<=', True)], context=context)
        for coord in coord_obj.browse(cr, SUPERUSER_ID, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                result[coord.partner_id.id] = 'VIP' if coord.vip else 'N/A: %s' % coord.email if coord.unauthorized else coord.email
        return result

    _email_store_trigger = {
       'email.coordinate': (lambda self, cr, uid, ids, context=None: self.pool['email.coordinate'].get_linked_partners(cr, uid, ids, context=context),
           ['partner_id', 'email', 'is_main', 'vip', 'unauthorized', 'active'], 10),
    }

    _columns = {
        'email_coordinate_ids': fields.one2many('email.coordinate', 'partner_id', 'Email Coordinates', domain=[('active', '=', True)], context={'force_recompute': True}),
        'email_coordinate_inactive_ids': fields.one2many('email.coordinate', 'partner_id', 'Email Coordinates', domain=[('active', '=', False)]),

        'email_coordinate_id': fields.function(_get_main_email_coordinate_ids, string='Email',
                                               type='many2one', relation="email.coordinate"),

        # Standard fields redefinition
        'email': fields.function(_get_main_email, string='Email',
                                 type='char', select=True,
                                 store=_email_store_trigger),
    }

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        """
        default = default or {}
        default.update({
            'email_coordinate_ids': [],
            'email_coordinate_inactive_ids': [],
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

