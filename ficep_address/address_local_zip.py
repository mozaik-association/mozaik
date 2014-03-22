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


class address_local_zip(orm.Model):

    _name = 'address.local.zip'
    _description = "Local Zip Code"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_linked_addresses(self, cr, uid, ids, context=None):
        return self.pool.get('address.address').search(cr, uid, [('address_local_zip_id', 'in', ids)], context=context)

    _columns = {
        'local_zip': fields.char(string='Zip Code', required=True, select=True, track_visibility='onchange'),
        'town': fields.char(string='Town', required=True, select=True, track_visibility='onchange'),
    }

    _rec_name = 'local_zip'

    _sql_constraints = [
        ('check_unicity_zip', 'unique(local_zip,town)', _('This zip code already exists!'))
    ]

    _order = "local_zip,town"

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
        for record in self.read(cr, uid, ids, [], context=context):
            display_name = "%s %s" % (record['local_zip'], record['town'])
            res.append((record['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, uid, ['|',('local_zip', operator, name),('town', operator, name)]+args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
