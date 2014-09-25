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
from openerp import tools


class virtual_mobile_partner(orm.Model):
    _name = "virtual.mobile.partner"
    _description = "Virtual Mobile Partner"
    _auto = False

    _columns = {
        'name': fields.char('Name'),
        'int_instance_id': fields.many2one(
            'int.instance', 'Internal Instance'),
        'phone': fields.char('Phone'),
        'email': fields.char('Email'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_mobile_partner')
        """
        Select partner_id and email from master partner
        and get phones of partners too
        Get Only row with at least a phone or an email
        """
        cr.execute("""
        create or replace view virtual_mobile_partner as (
        SELECT
            p.id as id,
            p.int_instance_id as int_instance_id,
            p.display_name as name,
            ph.name as phone,
            e.email as email
        FROM
            res_partner p
        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id)
        LEFT OUTER JOIN
            phone_coordinate phc
        ON (phc.partner_id = p.id)
        LEFT OUTER JOIN
            phone_phone ph
        ON (ph.id = phc.phone_id)
            )""")
