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

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.ficep_address.address_address import TRIGGER_FIELDS


class res_partner(orm.Model):

    _inherit = "res.partner"

    def _get_main_postal_coordinate_id(self, cr, uid, ids, name, args, context=None):
        """
        ==============================
        _get_main_postal_coordinate_id
        ==============================
        Reset main address field for a given address
        :param ids: partner ids for which the address number has to be recomputed
        :type name: char
        :rparam: dictionary for all partner ids with the requested main address number
        :rtype: dict {partner_id: main_address}
        Note:
        Calling and result convention: Single mode
        """
        result = {}.fromkeys(ids, False)
        coord_obj = self.pool['postal.coordinate']
        coordinate_ids = coord_obj.search(cr, SUPERUSER_ID, [('partner_id', 'in', ids),
                                                             ('is_main', '=', True),
                                                             ('active', '<=', True)], context=context)
        for coord in coord_obj.browse(cr, uid, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                result[coord.partner_id.id] = coord.id
        return result

    def _get_street2(self, cr, uid, ids, name, args, context=None):
        result = {}.fromkeys(ids, False)
        coord_obj = self.pool['postal.coordinate']
        coordinate_ids = coord_obj.search(cr, SUPERUSER_ID, [('partner_id', 'in', ids),
                                                             ('is_main', '=', True),
                                                             ('active', '<=', True)], context=context)
        for coord in coord_obj.browse(cr, uid, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                result[coord.partner_id.id] = coord.address_id.street2
        return result

    def _get_main_address_componant(self, cr, uid, ids, name, args, context=None):
        """
        ===========================
        _get_main_address_componant
        ===========================
        Reset address fields with corresponding main postal coordinate ids
        :param ids: partner ids for which new address fields have to be recomputed
        :type name: char
        :rparam: dictionary for all partner id with requested main coordinate ids
        :rtype: dict {partner_id:{'country_id': ...,
                                  'city': ...,
                                  ...,
                                 }}
        Note:
        Calling and result convention: Multiple mode
        """
        result = {}.fromkeys(ids, {key: False for key in ['country_id','zip','city','street','address',]})
        coord_obj = self.pool['postal.coordinate']
        coordinate_ids = coord_obj.search(cr, uid, [('partner_id', 'in', ids),
                                                    ('is_main', '=', True),
                                                    ('active', '<=', True)], context=context)
        for coord in coord_obj.browse(cr, uid, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                result[coord.partner_id.id] = {
                    'country_id': coord.address_id.country_id.id,
                    'zip': coord.address_id.zip,
                    'city': coord.address_id.city,
                    'street': coord.address_id.street,
                    'address': 'VIP' if coord.vip else 'N/A: %s' % coord.address_id.name if coord.unauthorized else coord.address_id.name,
                }
        return result

    _street2_store_triggers = {
        'postal.coordinate': (lambda self, cr, uid, ids, context=None: self.pool['postal.coordinate'].get_linked_partners(cr, uid, ids, context=context),
            ['partner_id', 'address_id', 'is_main', 'active'], 10),
        'address.address': (lambda self, cr, uid, ids, context=None: self.pool['address.address'].get_linked_partners(cr, uid, ids, context=context),
            ['street2'], 10),
     }

    _postal_store_triggers = {
        'postal.coordinate': (lambda self, cr, uid, ids, context=None: self.pool['postal.coordinate'].get_linked_partners(cr, uid, ids, context=context),
            ['partner_id', 'address_id', 'is_main', 'vip', 'unauthorized', 'active'], 10),
        'address.address': (lambda self, cr, uid, ids, context=None: self.pool['address.address'].get_linked_partners(cr, uid, ids, context=context),
            TRIGGER_FIELDS, 30),
        'address.local.zip': (lambda self, cr, uid, ids, context=None: self.pool['address.local.zip'].get_linked_partners(cr, uid, ids, context=context),
            ['local_zip', 'town'], 25),
        'address.local.street': (lambda self, cr, uid, ids, context=None: self.pool['address.local.street'].get_linked_partners(cr, uid, ids, context=context),
            ['local_street', 'local_street_alternative'], 25),
        'res.country': (lambda self, cr, uid, ids, context=None: self.pool['res.country'].get_linked_partners(cr, uid, ids, context=context),
            ['name'], 25),
     }

    _columns = {
        'postal_coordinate_ids': fields.one2many('postal.coordinate', 'partner_id', 'Postal Coordinates', domain=[('active', '=', True)]),
        'postal_coordinate_inactive_ids': fields.one2many('postal.coordinate', 'partner_id', 'Postal Coordinates', domain=[('active', '=', False)]),

        'postal_coordinate_id': fields.function(_get_main_postal_coordinate_id, string='Address',
                                                type='many2one', relation="postal.coordinate"),

        'address': fields.function(_get_main_address_componant, string='Address',
                                 type='char', select=True,
                                 multi='all_address_componant_in_one',
                                 store=_postal_store_triggers),

        # Standard fields redefinition
        'country_id': fields.function(_get_main_address_componant, string='Country',
                                 type='many2one', relation='res.country', select=True,
                                 multi='all_address_componant_in_one',
                                 store=_postal_store_triggers),
        'city': fields.function(_get_main_address_componant, string='City',
                                 type='char',
                                 multi='all_address_componant_in_one',
                                 store=_postal_store_triggers),
        'zip': fields.function(_get_main_address_componant, string='Zip Code',
                                 type='char',
                                 multi='all_address_componant_in_one',
                                 store=_postal_store_triggers),
        'street': fields.function(_get_main_address_componant, string='Street',
                                 type='char',
                                 multi='all_address_componant_in_one',
                                 store=_postal_store_triggers),
        'street2': fields.function(_get_street2, string='Street2',
                                 type='char',
                                 store=_street2_store_triggers),
    }

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        """
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default, context=context)
        res.update({
                    'postal_coordinate_ids': [],
                    'postal_coordinate_inactive_ids': [],
                   })
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        When invalidating a partner, invalidates also its postal coordinates
        """
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        if 'active' in vals and not vals['active']:
            coord_obj = self.pool['postal.coordinate']
            coord_ids = []
            for partner in self.browse(cr, SUPERUSER_ID, ids, context=context):
                coord_ids += [c.id for c in partner.postal_coordinate_ids]
            if coord_ids:
                coord_obj.button_invalidate(cr, SUPERUSER_ID, coord_ids, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
