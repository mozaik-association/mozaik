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


class address_local_zip(orm.Model):

    _name = 'address.local.zip'
    _inherit = ['mozaik.abstract.model']
    _description = 'Local Zip Code'

    def _get_linked_addresses(self, cr, uid, ids, context=None):
        return self.pool['address.address'].search(cr, uid, [('address_local_zip_id', 'in', ids)], context=context)

    _columns = {
        'local_zip': fields.char(string='Zip Code', required=True, select=True, track_visibility='onchange'),
        'town': fields.char(string='Town', required=True, select=True, track_visibility='onchange'),
    }

    _rec_name = 'local_zip'

    _order = "local_zip, town"

# constraints

    _unicity_keys = 'local_zip, town'

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        ========
        name_get
        ========
        :rparam: list of tuple (id, name to display)
                 where id is the id of the object into the relation
                 and display_name, the name of this object.
        :rtype: [(id,name)] list of tuple
        """
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.read(cr, uid, ids, ['local_zip', 'town'], context=context):
            display_name = "%s %s" % (record['local_zip'], record['town'])
            res.append((record['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, uid, ['|', ('local_zip', operator, name), ('town', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

# public methods

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Return all partners ids linked to local zip code ids
        :param: ids
        :type: list of local zip code ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        adr_ids = self._get_linked_addresses(cr, uid, ids, context=context)
        return self.pool['address.address'].get_linked_partners(cr, uid, adr_ids, context=context)

