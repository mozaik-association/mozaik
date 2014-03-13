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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
