# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_address, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_address is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_address is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_address.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields
from openerp.tools.translate import _


class address_local_street(orm.Model):

    _name = 'address.local.street'
    _description = "Local Street"

    def _get_linked_addresses(self, cr, uid, ids, context=None):
        return self.pool.get('address.address').search(
            cr, uid, [('address_local_street_id', 'in', ids)], context=context)

    _columns = {
        'local_zip': fields.char(string='Zip', required=True, select=True),
        'identifier': fields.char('Identifier', required=True, select=True),

        'local_street': fields.char(string='Street', required=True,
                                    select=True),
        'local_street_alternative': fields.char(string='Alternative Street',
                                                select=True),

        'disabled': fields.boolean(string='Disabled'),
        'write_date': fields.datetime('Last Update', readonly=True),
    }

    _rec_name = 'local_street'

    _sql_constraints = [
        ('check_unicity_street', 'unique(local_zip,identifier)',
         _('This local street identifier already exists for this zip code!'))
    ]

    _order = "local_zip,local_street"

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        If a ``local_street_alternative`` is defined then name must be show
        like this "local_street / local_street_alternative"
        """
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            display_name = ' / '.join([s for s in [
                record.local_street, record.local_street_alternative] if s])
            res.append((record['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(
                cr, uid, ['|',
                          ('local_street', operator, name),
                          ('local_street_alternative', operator, name)] + args,
                limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

# public methods

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Return all partners ids linked to local street ids
        :param: ids
        :type: list of local street ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        adr_ids = self._get_linked_addresses(cr, uid, ids, context=context)
        return self.pool['address.address'].get_linked_partners(
            cr, uid, adr_ids, context=context)
