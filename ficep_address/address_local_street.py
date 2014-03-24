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
    _description = "Local Streets Referential"

    def _get_linked_addresses(self, cr, uid, ids, context=None):
        return self.pool.get('address.address').search(cr, uid, [('address_local_street_id', 'in', ids)], context=context)

    _columns = {
        'local_street': fields.char(string='Street', required=True, select=True),
        'local_street_alternative': fields.char(string='Street Alternative', select=True),
        'local_zip': fields.char(string='Zip', required=True, select=True),
    }

    _rec_name = 'local_street'

    _sql_constraints = [
        ('check_unicity_street', 'unique(local_street,local_zip)', _('This local street already exist for this zip code!'))
    ]

    _order = "local_zip,local_street"

#orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        If an ``local_street_alternative`` is defined then name must be show
        like this "local_street / local_street_alternative"
        """
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            display_name = record.local_street if not record.local_street_alternative \
                           else ''.join([record.local_street, ' / ', \
                                   record.local_street_alternative])
            res.append((record['id'], display_name))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
