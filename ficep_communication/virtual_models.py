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
from openerp import tools
from openerp.osv import orm, fields


class virtual_partner_involvement(orm.Model):

    _name = "virtual.partner.involvement"
    _description = "Virtual Partner Involvement"
    _auto = False

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'involvement_id': fields.many2one('partner.involvement', 'Involvement'),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'display_name': fields.char('Partner Display Name'),
        'gender': fields.char('Partner Gender'),
        'tongue': fields.char('Partner Tongue'),

        'postal_vip': fields.boolean('Postal VIP'),
        'postal_unauthorized': fields.boolean('Postal Unauthorized'),

        'email_vip': fields.boolean('Email VIP'),
        'email_unauthorized': fields.boolean('Email Unauthorized'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_involvement')
        cr.execute("""
        create or replace view virtual_partner_involvement as (
        SELECT
            concat(p.id, pi.id) as id,
            pi.id as involvement_id,
            pi.partner_id as partner_id,
            p.display_name as display_name,
            p.gender as gender,
            p.tongue as tongue,
            p.int_instance_id as int_instance_id,
            pc.id as postal_coordinate_id,
            pc.vip as postal_vip,
            pc.unauthorized as postal_unauthorized,
            e.id as email_coordinate_id,
            e.unauthorized as email_unauthorized,
            e.vip as email_vip
        FROM
            partner_involvement pi
        JOIN
            res_partner p
        ON (pi.partner_id = p.id)

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = True
        AND pc.is_main = True)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = True
        AND e.is_main = True)
            )""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
