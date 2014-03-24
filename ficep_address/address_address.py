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
from collections import OrderedDict
from openerp.osv import orm, fields
from openerp.tools.translate import _

COUNTRY_CODE = 'BE'
# Do Not Add Sequence Here
TRIGGER_FIELDS = OrderedDict([('country_id', 'id'),
                              ('address_local_zip_id', 'id'),
                              ('zip_man', False),
                              ('town_man', False),
                              ('address_local_street_id', 'id'),
                              ('street_man', False),
                              ('zip_man', False),
                              ('town_man', False),
                              ('number', False),
                              ('box', False), ])


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
        result = dict((i, {}) for i in ids)
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            complete_number = '%s' % adrs.number if adrs.number else '-'
            complete_number = '%s/%s' % (complete_number, adrs.box) if \
                              adrs.box else '%s(%s)' % (complete_number, adrs.sequence)
            elts = [complete_number,
                    adrs.street,
                    '-',
                    (adrs.country_code == 'BE') and adrs.zip or False,
                    adrs.city or False,
                    (adrs.country_code != 'BE') and '-' or False,
                    (adrs.country_code != 'BE') and adrs.country_id.name or False,
                   ]
            adr = ' '.join([el for el in elts if el])
            result[adrs.id]['name'] = adr or False
        for adrs in adrs_recs:
            technical_value = []
            for field in TRIGGER_FIELDS.keys():
                to_evaluate = field if not TRIGGER_FIELDS[field] else '%s.%s' % (field, TRIGGER_FIELDS[field])
                value = eval('adrs.%s' % to_evaluate)
                if value:
                    technical_value.append(str(value))
            # add sequence
            if adrs.sequence:
                technical_value.append(str(adrs.sequence))
            technical_name = '#'.join(technical_value)
            result[adrs.id]['technical_name'] = technical_name or False
        return result

    def _get_street(self, cr, uid, ids, name, args, context=None):
        result = {}.fromkeys(ids, False)
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            result[adrs.id] = adrs.address_local_street_id and adrs.select_alternative_address_local_street and \
                              adrs.address_local_street_id.local_street_alternative and \
                              adrs.address_local_street_id.local_street_alternative or \
                              adrs.address_local_street_id and not adrs.select_alternative_address_local_street and \
                              adrs.address_local_street_id.local_street or \
                              adrs.street_man or False

        return result

    def _get_zip(self, cr, uid, ids, name, args, context=None):
        result = dict((i, {}) for i in ids)
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            result[adrs.id]['zip'] = adrs.address_local_zip_id and adrs.address_local_zip_id.local_zip or adrs.zip_man or False
            result[adrs.id]['city'] = adrs.address_local_zip_id and adrs.address_local_zip_id.town or adrs.town_man or False

        return result

    _address_store_triggers = {
            # this MUST be executed in last for consistency: sequence is greater than other
            'address.address': (lambda self, cr, uid, ids, context=None: ids, [], 11),
            'res.country': (_get_linked_addresses_from_country, ['name'], 10),
    }
    _zip_store_triggers = {
            'address.address': (lambda self, cr, uid, ids, context=None: ids, ['address_local_zip_id', 'zip_man', 'town_man'], 10),
            'address.local.zip': (_get_linked_addresses_from_local_zip, [], 10),
    }
    _street_store_triggers = {
            'address.address': (lambda self, cr, uid, ids, context=None: ids, ['address_local_street_id', 'street_man', 'select_alternative_address_local_street'], 10),
            'address.local.street': (_get_linked_addresses_from_local_street, ['local_street'], 10),
    }

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.function(_get_integral_address, string='Address', type='char',
                                store=_address_store_triggers, multi='display_and_technical'),
        'technical_name': fields.function(_get_integral_address, string='Technical Name', type='char',
                                store=_address_store_triggers, multi='display_and_technical'),
        'country_id': fields.many2one('res.country', 'Country', required=True, track_visibility='onchange'),
        'country_code': fields.related('country_id', 'code', string='Country Code', type='char'),

        'zip': fields.function(_get_zip, string='Zip', type='char', multi='ZipAndCity',
                                store=_zip_store_triggers),
        'address_local_zip_id': fields.many2one('address.local.zip', string='City', track_visibility='onchange'),
        'zip_man': fields.char(string='Zip', track_visibility='onchange'),

        'city': fields.function(_get_zip, string='City', type='char', multi='ZipAndCity',
                                store=_zip_store_triggers),
        'town_man': fields.char(string='Town', track_visibility='onchange'),

        'street': fields.function(_get_street,
                                  string='Street',
                                  type='char',
                                  store=_street_store_triggers),
        'address_local_street_id': fields.many2one('address.local.street', string='Referenced Street', track_visibility='onchange'),
        'street_man': fields.char(string='Street', track_visibility='onchange'),

        'select_alternative_address_local_street': fields.boolean('Select Alternative Referenced Street Name'),

        'street2': fields.char(string='Street2', track_visibility='onchange'),
        'number': fields.char(string='Number', track_visibility='onchange'),
        'box': fields.char(string='Box', track_visibility='onchange'),

        'sequence': fields.integer('Sequence'),
        'postal_coordinate_ids': fields.one2many('postal.coordinate', 'address_id', 'Postal Coordinates'),
    }

    _defaults = {
        'sequence': 0,
        'country_id': lambda self, cr, uid, c:
        self.pool.get('res.country')._country_default_get(cr, uid, COUNTRY_CODE, context=c),
        'country_code': COUNTRY_CODE,
    }

    _sql_constraints = [
        ('check_unicity_number', 'unique(technical_name)', _('This Address already exists!'))
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
                                if country_id else False,
                'address_local_zip_id': False,
             }
        }

    def onchange_local_zip_id(self, cr, uid, ids, local_zip_id, context=None):
        zip, city = False, False
        if local_zip_id:
            zip_city = self.pool.get('address.local.zip').read(cr, uid, [local_zip_id], [], context=context)[0]
            zip, city = zip_city['local_zip'], zip_city['town']
        return {
            'value': {
                'zip': zip,
                'city': city,
                'zip_man': False,
                'town_man': False,
                'address_local_street_id': False,
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
            for associated_coordinate in record.postal_coordinate_ids:
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
    _description = "Postal Coordinate"

    _discriminant_field = 'address_id'
    _undo_redirect_action = 'ficep_address.postal_coordinate_action'

    _columns = {
        'address_id': fields.many2one('address.address', string='Address', required=True, readonly=True, select=True),
        'co_residency_id': fields.many2one('co.residency', string='Co-residency', ondelete='restrict'),
    }

    _rec_name = _discriminant_field

    def _check_co_residency_consistency(self, cr, uid, ids, context=None):
        postal_coordinates = self.browse(cr, uid, ids, context=context)
        for postal_coordinate in postal_coordinates:
            if postal_coordinate.co_residency_id:
                postal_co_resident_ids = self.search(cr, uid, [('co_residency_id', '=', postal_coordinate.co_residency_id.id)], context=context)
                address_ids = [(postal_coo.address_id.id) for postal_coo in self.browse(cr, uid, postal_co_resident_ids)]
                if len(set(address_ids)) != 1:
                    return False
        return True

    _constraints = [
        (_check_co_residency_consistency, _('Co-Residency Could Not Be Associated With Different Address Of Postal Coordinate'),
        ['co_residency_id']),
    ]


class co_residency(orm.Model):
    _name = 'co.residency'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'id': fields.integer('ID'),
        'name': fields.char('Name', track_visibility='onchange'),
        'line': fields.char('Line', track_visibility='onchange'),
        'line2': fields.char('Line 2', track_visibility='onchange'),
        'postal_coordinate_ids': fields.one2many('postal.coordinate',
                                                 'address_id',
                                                 'Postal Coordinates',
                                                 domain=[('active', '=', True)],
                                                 track_visibility='onchange'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
