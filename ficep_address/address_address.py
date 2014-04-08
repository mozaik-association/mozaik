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
import unicodedata
import re

from collections import OrderedDict
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID

NOT_ALPHANUMERICS = re.compile('[^\da-zA-Z]+')
BLANK = re.compile('  +')

COUNTRY_CODE = 'BE'
# Do Not Add Sequence Here
KEY_FIELDS = OrderedDict([
    ('country_id', 'id'),
    ('address_local_zip_id', 'id'),
    ('zip_man', False),
    ('town_man', False),
    ('address_local_street_id', 'id'),
    ('street_man', False),
    ('number', False),
    ('box', False),
])
TRIGGER_FIELDS = KEY_FIELDS.keys() + ['sequence', 'select_alternative_address_local_street']


class address_address(orm.Model):

    _name = 'address.address'
    _description = "Address"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

# private methods

    def _get_linked_coordinates(self, cr, uid, ids, context=None):
        return self.pool['postal.coordinate'].search(cr, uid, [('address_id', 'in', ids)], context=context)

    def _get_integral_address(self, cr, uid, ids, name, args, context=None):
        result = {}.fromkeys(ids, {key: False for key in ['name', 'technical_name', ]})
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            elts = [
                adrs.sequence and '[%s]:' % adrs.sequence or False,
                adrs.street or False,
                adrs.street and '-' or False,
                (adrs.country_code == 'BE') and adrs.zip or False,
                adrs.city or False,
                (adrs.country_code != 'BE') and '-' or False,
                (adrs.country_code != 'BE') and adrs.country_id.name or False,
            ]
            adr = ' '.join([el for el in elts if el])

            technical_value = []
            for field in KEY_FIELDS.keys():
                to_evaluate = field if not KEY_FIELDS[field] else '%s.%s' % (field, KEY_FIELDS[field])
                value = eval('adrs.%s' % to_evaluate)
                technical_value.append(self.format_value(cr, uid, str(value or 0), context=context))
            technical_name = '#'.join(technical_value)

            result[adrs.id] = {
                'name': adr or False,
                'technical_name': technical_name or False,
            }
        return result

    def _get_street(self, cr, uid, ids, name, args, context=None):
        result = {}.fromkeys(ids, False)
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            number = adrs.number or '-'
            number = adrs.box and '%s/%s' % (number, adrs.box) or \
                     adrs.number or False
            if adrs.address_local_street_id:
                street = adrs.select_alternative_address_local_street and \
                         adrs.address_local_street_id.local_street_alternative or \
                         adrs.address_local_street_id.local_street
            else:
                street = adrs.street_man or False
            result[adrs.id] = ' '.join([el for el in [number, street] if el])

        return result

    def _get_zip(self, cr, uid, ids, name, args, context=None):
        result = {}.fromkeys(ids, {key: False for key in ['zip', 'city', ]})
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            result[adrs.id] = {
                'zip': adrs.address_local_zip_id and adrs.address_local_zip_id.local_zip or adrs.zip_man or False,
                'city': adrs.address_local_zip_id and adrs.address_local_zip_id.town or adrs.town_man or False,
            }

        return result

    _address_store_triggers = {
        # this MUST be executed in last for consistency: sequence is greater than other
        'address.address': (lambda self, cr, uid, ids, context=None: ids,
            TRIGGER_FIELDS, 20),
        'address.local.zip': (lambda self, cr, uid, ids, context=None: self.pool['address.local.zip']._get_linked_addresses(cr, uid, ids, context=context),
            ['local_zip', 'town'], 15),
        'address.local.street': (lambda self, cr, uid, ids, context=None: self.pool['address.local.street']._get_linked_addresses(cr, uid, ids, context=context),
            ['local_street', 'local_street_alternative'], 15),
        'res.country': (lambda self, cr, uid, ids, context=None: self.pool['res.country']._get_linked_addresses(cr, uid, ids, context=context),
            ['name'], 15),
    }
    _zip_store_triggers = {
        'address.address': (lambda self, cr, uid, ids, context=None: ids,
            ['address_local_zip_id', 'zip_man', 'town_man'], 10),
        'address.local.zip': (lambda self, cr, uid, ids, context=None: self.pool['address.local.zip']._get_linked_addresses(cr, uid, ids, context=context),
            ['local_zip', 'town'], 10),
    }
    _street_store_triggers = {
        'address.address': (lambda self, cr, uid, ids, context=None: ids,
            ['address_local_street_id', 'select_alternative_address_local_street', 'street_man', 'number', 'box'], 10),
        'address.local.street': (lambda self, cr, uid, ids, context=None: self.pool['address.local.street']._get_linked_addresses(cr, uid, ids, context=context),
            ['local_street', 'local_street_alternative'], 10),
    }

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.function(_get_integral_address, string='Address', type='char', select=True,
                                multi='display_and_technical', store=_address_store_triggers),
        'technical_name': fields.function(_get_integral_address, string='Technical Name', type='char', select=True,
                                multi='display_and_technical', store=_address_store_triggers),

        'country_id': fields.many2one('res.country', 'Country', required=True, select=True, track_visibility='onchange'),
        'country_code': fields.related('country_id', 'code', string='Country Code', type='char'),

        'zip': fields.function(_get_zip, string='Zip', type='char',
                               multi='ZipAndCity', store=_zip_store_triggers),
        'address_local_zip_id': fields.many2one('address.local.zip', string='City', track_visibility='onchange'),
        'zip_man': fields.char(string='Zip', track_visibility='onchange'),

        'city': fields.function(_get_zip, string='City', type='char',
                                multi='ZipAndCity', store=_zip_store_triggers),
        'town_man': fields.char(string='Town', track_visibility='onchange'),

        'street': fields.function(_get_street, string='Street', type='char',
                                  store=_street_store_triggers),
        'address_local_street_id': fields.many2one('address.local.street', string='Reference Street', track_visibility='onchange'),
        'select_alternative_address_local_street': fields.boolean('Use Alternative Reference Street', track_visibility='onchange'),
        'street_man': fields.char(string='Street', track_visibility='onchange'),

        'street2': fields.char(string='Street2', track_visibility='onchange'),

        'number': fields.char(string='Number', track_visibility='onchange'),
        'box': fields.char(string='Box', track_visibility='onchange'),
        'sequence': fields.integer('Sequence', track_visibility='onchange'),

        'postal_coordinate_ids': fields.one2many('postal.coordinate', 'address_id', 'Postal Coordinates'),
    }

    _defaults = {
        'country_id': lambda self, cr, uid, c:
            self.pool.get('res.country')._country_default_get(cr, uid, COUNTRY_CODE, context=c),
        'country_code': COUNTRY_CODE,
        'sequence': 0,
    }

    _sql_constraints = [
        ('check_unicity_address', 'unique(technical_name,sequence)', _('This Address already exists!'))
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
            res.append((record['id'], record['name']))
        return res

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Increase sequence value when duplicating address
        """
        adr_id = isinstance(ids, (long, int)) and [ids] or ids
        technical_name = self.read(cr, uid, adr_id[0], ['technical_name'], context=context)['technical_name']
        cr.execute('SELECT MAX(sequence) FROM %s WHERE technical_name=%%s' % (self._table,), (technical_name,))
        sequence = cr.fetchone()
        sequence = sequence and sequence[0] or False
        if not sequence:
            raise orm.except_orm(_('Error'), _('An Address without sequence number cannot be duplicated!'))

        default = dict(default or {})
        default.update({
            'sequence': sequence + 1,
            'postal_coordinate_ids': [],
        })
        res = super(address_address, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

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
        _zip, city = False, False
        if local_zip_id:
            zip_city = self.pool.get('address.local.zip').read(cr, uid, [local_zip_id], [], context=context)[0]
            _zip, city = zip_city['local_zip'], zip_city['town']
        return {
            'value': {
                'zip': _zip,
                'city': city,
                'zip_man': False,
                'town_man': False,
             }
        }

    def onchange_zip(self, cr, uid, ids, _zip, context=None):
        return {
            'value': {
                'address_local_street_id': False,
             }
        }

    def onchange_local_street_id(self, cr, uid, ids, local_street_id, context=None):
        vals = {} if local_street_id else {'select_alternative_address_local_street': False}
        vals.update({'street_man': False})
        return {
            'value': vals
        }

# public methods

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Return all partners ids linked to addresses ids
        :param: ids
        :type: list of addresses ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        coord_ids = self._get_linked_coordinates(cr, uid, ids, context=context)
        return self.pool['postal.coordinate'].get_linked_partners(cr, uid, coord_ids, context=context)

    def format_value(self, cr, uid, value, context=None):
        """
        ============
        format_value
        ============
        :type value: char
        :rtype: char
        :rparam: upper to lower case for value and deletion of accented character
        """
        value = ''.join(c for c in unicodedata.normalize('NFD', u'%s' % value)
                  if unicodedata.category(c) != 'Mn')
        value = re.sub(NOT_ALPHANUMERICS, ' ', value)
        value = re.sub(BLANK, ' ', value)
        return value.lower().strip()


class postal_coordinate(orm.Model):

    _name = 'postal.coordinate'
    _inherit = ['abstract.coordinate']
    _description = "Postal Coordinate"

    _discriminant_field = 'address_id'
    _trigger_fileds = []
    _undo_redirect_action = 'ficep_address.postal_coordinate_action'

    _columns = {
        'address_id': fields.many2one('address.address', string='Address', required=True, readonly=True, select=True),
        'co_residency_id': fields.many2one('co.residency', string='Co-Residency', select=True, ondelete='restrict', track_visibility='onchange'),
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
        (_check_co_residency_consistency, _('Co-Residency could not be associated to Postal Coordinates related to more than one Address'),
        ['co_residency_id']),
    ]

# orm methods

    def create(self, cr, uid, vals, context=None):
        if vals.get('co_residency_id', False):
            if not self.search(cr, SUPERUSER_ID, [('co_residency_id', '=', vals['co_residency_id'])], context=context):
                vals['co_residency_id'] = False
        return super(postal_coordinate, self).create(cr, uid, vals, context=context)

# public methods

    def get_fields_to_update(self, cr, uid, mode, context=None):
        """
        ====================
        get_fields_to_update
        ====================
        :type mode: char
        :param mode: is the mode that define the return value
        :rtype: dictionary
        :rparam: if mode is duplicate then return
            {'is_duplicate_detected': True,
             'is_duplicate_allowed': False,
             'co_residency_id': False,
            }
        """
        res = super(postal_coordinate, self).get_fields_to_update(cr, uid, mode, context=context)
        if mode == 'duplicate' or mode == 'reset':
            res.update({'co_residency_id': False})
        return res


class co_residency(orm.Model):
    _name = 'co.residency'
    _inherit = ['abstract.ficep.model']
    _description = "Co-Residency"

    _columns = {
        'name': fields.char('Name', required=True, select=True, track_visibility='onchange'),
        'line': fields.char('Line 1', track_visibility='onchange'),
        'line2': fields.char('Line 2', track_visibility='onchange'),
        'postal_coordinate_ids': fields.one2many('postal.coordinate', 'co_residency_id', string='Postal Coordinates',
                                                 domain=[('active', '=', True)]),
        'postal_coordinate_inactive_ids': fields.one2many('postal.coordinate', 'co_residency_id', string='Postal Coordinates',
                                                 domain=[('active', '=', False)]),
    }

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        """
        default = default or {}
        default.update({
            'postal_coordinate_ids': [],
            'postal_coordinate_inactive_ids': [],
        })
        res = super(co_residency, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
