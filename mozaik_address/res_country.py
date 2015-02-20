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
from openerp.osv import orm


class res_country(orm.Model):

    _inherit = "res.country"

    def _country_default_get(self, cr, uid, country_code, context=None):
        country_id = self.search(cr, uid, [('code', '=', country_code)], context=context)
        if country_id:
            return country_id[0]
        return False

    def _get_linked_addresses(self, cr, uid, ids, context=None):
        return self.pool.get('address.address').search(cr, uid, [('country_id', 'in', ids)], context=context)

# public methods

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Return all partners ids linked to country ids
        :param: ids
        :type: list of country ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        adr_ids = self._get_linked_addresses(cr, uid, ids, context=context)
        return self.pool['address.address'].get_linked_partners(cr, uid, adr_ids, context=context)

