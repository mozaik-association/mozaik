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


class ficep_coordinate(orm.AbstractModel):

    _name = 'ficep.coordinate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _coordinate_field = None

    _columns = {
        'id': fields.integer('ID', readonly=True),

        'partner_id': fields.many2one('res.partner', 'Contact', readonly=True, required=True, select=True),
        'coordinate_category_id': fields.many2one('coordinate.category', 'Coordinate Category', select=True, track_visibility='onchange'),

        'is_main': fields.boolean('Is Main', readonly=True, select=True),
        'unauthorized': fields.boolean('Unauthorized', track_visibility='onchange'),
        'vip': fields.boolean('VIP', track_visibility='onchange'),

        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', readonly=True, track_visibility='onchange'),
        'active': fields.boolean('Active', readonly=True),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
