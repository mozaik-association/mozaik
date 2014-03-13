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
from openerp.tools.translate import _


class address_local_street(orm.Model):

    _name = 'address.local.street'
    _description = "Address Local Street"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_linked_addresses(self, cr, uid, ids, context=None):
        return self.pool.get('address.address').search(cr, uid, [('address_local_street_id', 'in', ids)], context=context)

    _columns = {
        'local_street': fields.char('Street', size=50, required=True, select=True, track_visibility='onchange'),
        'local_zip_id': fields.many2one('address.local.zip', 'local_zip', 'Local Zip'),
    }

    _rec_name = 'local_street'

    _sql_constraints = [
        ('check_unicity_street', 'unique(local_street,local_zip_id)', _('This street already exist for this given zip code!'))
    ]

    _order = "local_street"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
