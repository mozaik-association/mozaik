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

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields


class res_partner(orm.Model):

    _inherit = "res.partner"

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
        result = {}.fromkeys(ids, False)
        coord_obj = self.pool['email.coordinate']
        coordinate_ids = coord_obj.search(cr, uid, [('partner_id', 'in', ids),
                                                    ('is_main', '=', True),
                                                    ('active', '<=', True)], context=context)
        for coord in coord_obj.browse(cr, uid, coordinate_ids, context=context):
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
        result = {}.fromkeys(ids, False)
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
        'email_coordinate_ids': fields.one2many('email.coordinate', 'partner_id', 'Email Coordinates', domain=[('active', '=', True)]),
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

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        When invalidating a partner, invalidates also its email coordinates
        """
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        if 'active' in vals and not vals['active']:
            coord_obj = self.pool['email.coordinate']
            coord_ids = []
            for partner in self.browse(cr, SUPERUSER_ID, ids, context=context):
                coord_ids += [c.id for c in partner.email_coordinate_ids]
            if coord_ids:
                coord_obj.button_invalidate(cr, SUPERUSER_ID, coord_ids, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
