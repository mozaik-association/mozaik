# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mobile, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mobile is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mobile is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mobile.
#     If not, see <http://www.gnu.org/licenses/>.
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
            'int.instance', string='Internal Instance'),
        'phone': fields.char('Phone'),
        'email': fields.char('Email'),
    }

# orm methods

    def init(self, cr):
        """
        Select partner_id and email from master partner
        and get phones of partners too
        Get Only row with at least a phone or an email
        """
        tools.drop_view_if_exists(cr, 'virtual_mobile_partner')
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
        ON (e.partner_id = p.id
        AND e.active IS TRUE)
        LEFT OUTER JOIN
            phone_coordinate phc
        ON (phc.partner_id = p.id
        AND phc.active IS TRUE)
        LEFT OUTER JOIN
            phone_phone ph
        ON (ph.id = phc.phone_id
        AND ph.active IS TRUE)
        WHERE p.active IS TRUE
            )""")
