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

COUNTRY_CODE = 'BE'


class address_address(orm.Model):

    _name = 'address.address'
    _description = "Address"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

# private methods

    def _get_linked_addresses_from_country(self, cr, uid, ids, context=None):
        return self.pool.get('res.country')._get_linked_addresses(cr, uid, ids, context=context)

    def _get_linked_addresses_from_local_zip(self, cr, uid, ids, context=None):
        return self.pool.get('address.local.zip')._get_linked_addresses(cr, uid, ids, context=context)

    def _get_linked_addresses_from_local_street(self, cr, uid, ids, context=None):
        return self.pool.get('address.local.street')._get_linked_addresses(cr, uid, ids, context=context)

    def _get_integral_address(self, cr, uid, ids, name, args, context=None):
        result = {}.fromkeys(ids, False)
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            real_address_value = ''
            if adrs.number:
                real_address_value = ''.join([real_address_value, '%s ' % adrs.number])
            if adrs.box:
                real_address_value = ''.join([real_address_value, '%s ' % adrs.box])
            if adrs.street:
                real_address_value = ''.join([real_address_value, '%s ' % adrs.street])
            if adrs.street2:
                real_address_value = ''.join([real_address_value, '%s ' % adrs.street2])
            if adrs.address_local_zip_id:
                real_address_value = ''.join([real_address_value, '%s ' % adrs.address_local_zip_id.local_zip])
            if adrs.country_id:
                real_address_value = ''.join([real_address_value, '%s ' % adrs.country_id.name])
            result[adrs.id] = real_address_value
        return result

    _address_store_triggers = {
            'address.address': (lambda self, cr, uid, ids, context=None: ids, [], 10),
            'res.country': (_get_linked_addresses_from_country, ['name'], 10),
            'address.local.zip': (_get_linked_addresses_from_local_zip, ['local_zip'], 10),
            'address.local.street': (_get_linked_addresses_from_local_street, ['local_street'], 10),
        }

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.function(_get_integral_address,
                                string='Address',
                                type='char',
                                store=_address_store_triggers),
        'country_id': fields.many2one('res.country', 'Country', track_visibility='onchange'),
        'country_code': fields.related('country_id', 'code', string='Country Code', type='char', relation='res.country'),

        'zip': fields.char('Zip'),
        'zip_man': fields.char('Zip'),
        'address_local_zip_id': fields.many2one('address.local.zip', 'Zip', track_visibility='onchange'),

        'town': fields.char('Town'),
        'town_man': fields.char('Town'),
        'address_local_zip_town': fields.related('address_local_zip_id', 'town', string="Town", type="char", relation="address.local.zip"),

        'street': fields.char('Street', track_visibility='onchange'),
        'street_man': fields.char('Street', track_visibility='onchange'),
        'address_local_street_id': fields.many2one('address.local.street', 'Street', track_visibility='onchange'),

        'street2': fields.char('Street2', track_visibility='onchange'),
        'number': fields.char('Number', track_visibility='onchange'),
        'box': fields.char('Box', track_visibility='onchange'),

        'postal_coordinate_ids': fields.one2many('postal.coordinate', 'address_id', 'Postal Coordinate'),
    }

    _defaults = {
        'country_id': lambda self, cr, uid, c:
        self.pool.get('res.country')._country_default_get(cr, uid, COUNTRY_CODE, context=c),
        'country_code': COUNTRY_CODE,
    }

    _sql_constraints = [
        ('check_unicity_number', 'unique(name)', _('This Address number already exists!'))
    ]

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
        for record in self.read(cr, uid, ids, ['name'], context=context):
            display_name = "%s" % (record['name'])
            res.append((record['id'], display_name))
        return res

    def copy(self, cr, uid, ids, default=None, context=None):
        """
        ====================
        copy address.address
        ====================
        Due to the constraint: to avoid the standard except: better explanation
        for the user
        """
        raise orm.except_orm(_('Error'), _('An Address cannot be duplicated!'))

# view methods: onchange, button

    def onchange_country_id(self, cr, uid, ids, country_id, context=None):
        return {
                'value': {
                          'country_code': self.pool.get('res.country').read(cr, uid, \
                                          [country_id], ['code'], context=context)[0]['code']
                                          if country_id else country_id,
                          'address_local_zip_id': False,
                          'address_local_zip_town': False,
                          'address_local_street_id': False,
                 }
        }

    def onchange_local_zip_id(self, cr, uid, ids, local_zip_id, context=None):
        return {
                'value': {
                          'address_local_street_id': False,
                          'address_local_zip_town': self.pool.get('address.local.zip').read(cr, uid, \
                                          [local_zip_id], ['town'], context=context)[0]['town']
                                          if local_zip_id else local_zip_id,
                          'town_man': False,
                          'zip_man': False,
                 }
        }

    def onchange_local_street_id(self, cr, uid, ids, local_street_id, context=None):
        return {
                'value': {
                          'street_man': False,
                 }
        }

# public methods

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Return partner ids linked to all related coordinate linked to address ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        address_rds = self.browse(cr, uid, ids, context=context)
        partner_ids = []
        for record in address_rds:
            for associated_coordinate in record.phone_coordinate_ids:
                partner_ids.append(associated_coordinate.partner_id.id)
        return partner_ids

    def get_linked_address_coordinates(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_address_coordinates
        ==============================
        Return address coordinate ids linked to address ids
        :rparam: address_coordinate_ids
        :rtype: list of ids
        """
        addresses = self.read(cr, uid, ids, ['address_coordinate_ids'], context=context)
        res_ids = []
        for address in addresses:
            res_ids += address['address_coordinate_ids']
        return list(set(res_ids))


class postal_coordinate(orm.Model):

    _name = 'postal.coordinate'
    _inherit = ['abstract.coordinate']
    _description = "Address Coordinate"

    _discriminant_field = 'address_id'
    _undo_redirect_action = 'ficep_phone.phone_coordinate_action'

    _columns = {
        'address_id': fields.many2one('address.address', string='Address', required=True, readonly=True, select=True),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
