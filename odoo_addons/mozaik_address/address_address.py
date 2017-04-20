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
from collections import OrderedDict

from openerp.osv import orm, fields
from openerp.tools.translate import _

from openerp.addons.mozaik_base.base_tools import format_value

COUNTRY_CODE = 'BE'
# Do Not Add Sequence Here
KEY_FIELDS = OrderedDict([
    ('country_id', 'id'),
    ('address_local_zip_id', 'local_zip'),
    ('zip_man', False),
    ('town_man', False),
    ('address_local_street_id', 'id'),
    ('street_man', False),
    ('number', False),
    ('box', False),
])
TRIGGER_FIELDS = KEY_FIELDS.keys() + [
    'sequence', 'select_alternative_address_local_street']


class address_address(orm.Model):

    _name = 'address.address'
    _inherit = ['mozaik.abstract.model']
    _description = 'Address'

# private methods

    def _get_technical_name(self, cr, uid, values, context=None):
        """
        This method produces a technical name with the content of values.
        :type values: dictionary
        :param values: used to create a technical address name
            ``country_id``
            ``address_local_zip``
            ``zip_man``
            ``town_man``
            ``address_local_street_id``
            ``street_man``
            ``number``
            ``box``
        :rparam: formated values of ``values`` join wit a `#`.
                0 if value is null
        """
        technical_value = []
        for field in values.keys():
            value = values[field] or u'0'
            technical_value.append(format_value(value))
        return '#'.join(technical_value)

    def _get_linked_coordinates(self, cr, uid, ids, context=None):
        return self.pool['postal.coordinate'].search(
            cr, uid, [('address_id', 'in', ids)], context=context)

    def _get_integral_address(self, cr, uid, ids, name, args, context=None):
        result = {i: {
            key: False for key in ['name', 'technical_name']} for i in ids}
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            elts = [
                adrs.street or False,
                adrs.sequence and '[%s]' % adrs.sequence or False,
                adrs.street and '-' or adrs.sequence and '-' or False,
                (adrs.country_code == 'BE') and adrs.zip or False,
                adrs.city or False,
                (adrs.country_code != 'BE') and '-' or False,
                (adrs.country_code != 'BE') and adrs.country_id.name or False,
            ]
            adr = ' '.join([el for el in elts if el])

            values = KEY_FIELDS.copy()
            for field in KEY_FIELDS.keys():
                to_evaluate = field if not KEY_FIELDS[field] else '%s.%s' % (
                    field, KEY_FIELDS[field])
                real_value = eval('adrs.%s' % to_evaluate)
                values[field] = real_value
            technical_name = self._get_technical_name(
                cr, uid, values, context=context)

            result[adrs.id] = {
                'name': adr or False,
                'technical_name': technical_name or False,
            }
        return result

    def _get_street(self, cr, uid, ids, name, args, context=None):
        result = {i: False for i in ids}
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
            result[adrs.id] = ' '.join([el for el in [street, number] if el])

        return result

    def _get_zip(self, cr, uid, ids, name, args, context=None):
        result = {i: {key: False for key in ['zip', 'city', ]} for i in ids}
        adrs_recs = self.browse(cr, uid, ids, context=context)
        for adrs in adrs_recs:
            result[adrs.id] = {
                'zip':
                    adrs.address_local_zip_id and
                    adrs.address_local_zip_id.local_zip or
                    adrs.zip_man or False,
                'city':
                    adrs.address_local_zip_id and
                    adrs.address_local_zip_id.town or
                    adrs.town_man or
                    False,
            }

        return result

    _address_store_triggers = {
        # this MUST be executed in last for consistency: sequence is greater
        # than other
        'address.address':
            (lambda self, cr, uid, ids, context=None: ids, TRIGGER_FIELDS, 20),
        'address.local.zip':
            (lambda self, cr, uid, ids, context=None:
             self.pool['address.local.zip']._get_linked_addresses(
                 cr, uid, ids, context=context),
             ['local_zip', 'town'], 15),
        'address.local.street':
            (lambda self, cr, uid, ids, context=None:
             self.pool['address.local.street']._get_linked_addresses(
                 cr, uid, ids, context=context),
             ['local_street', 'local_street_alternative'], 15),
        'res.country':
            (lambda self, cr, uid, ids, context=None:
             self.pool['res.country']._get_linked_addresses(
                 cr, uid, ids, context=context),
             ['name'], 15),
    }
    _zip_store_triggers = {
        'address.address':
            (lambda self, cr, uid, ids, context=None: ids,
             ['address_local_zip_id', 'zip_man', 'town_man'], 10),
        'address.local.zip':
            (lambda self, cr, uid, ids, context=None:
             self.pool['address.local.zip']._get_linked_addresses(
                 cr, uid, ids, context=context),
             ['local_zip', 'town'], 10),
    }
    _street_store_triggers = {
        'address.address':
            (lambda self, cr, uid, ids, context=None: ids,
             ['address_local_street_id',
              'select_alternative_address_local_street',
              'street_man', 'number', 'box'], 10),
        'address.local.street':
            (lambda self, cr, uid, ids, context=None:
             self.pool['address.local.street']._get_linked_addresses(
                 cr, uid, ids, context=context),
             ['local_street', 'local_street_alternative'], 10),
    }

    _columns = {
        'id':
            fields.integer('ID', readonly=True),
        'name':
            fields.function(
                _get_integral_address, string='Address', type='char',
                select=True, multi='display_and_technical',
                store=_address_store_triggers),
        'technical_name':
            fields.function(
                _get_integral_address, string='Technical Name', type='char',
                select=True, multi='display_and_technical',
                store=_address_store_triggers),

        'country_id':
            fields.many2one(
                'res.country', 'Country', required=True, select=True,
                track_visibility='onchange'),
        'country_code':
            fields.related(
                'country_id', 'code', string='Country Code', type='char'),

        'zip':
            fields.function(
                _get_zip, string='Zip', type='char', multi='ZipAndCity',
                store=_zip_store_triggers),
        'address_local_zip_id':
            fields.many2one(
                'address.local.zip', string='City',
                track_visibility='onchange'),
        'zip_man':
            fields.char(string='Zip', track_visibility='onchange'),

        'city':
            fields.function(
                _get_zip, string='City', type='char', multi='ZipAndCity',
                store=_zip_store_triggers),
        'town_man':
            fields.char(string='Town', track_visibility='onchange'),

        'street':
            fields.function(
                _get_street, string='Street', type='char',
                store=_street_store_triggers),
        'address_local_street_id':
            fields.many2one(
                'address.local.street', string='Reference Street',
                track_visibility='onchange'),
        'select_alternative_address_local_street':
            fields.boolean(
                'Use Alternative Reference Street',
                track_visibility='onchange'),
        'street_man':
            fields.char(string='Street', track_visibility='onchange'),
        'street2':
            fields.char(string='Street2', track_visibility='onchange'),

        'number':
            fields.char(string='Number', track_visibility='onchange'),
        'box':
            fields.char(string='Box', track_visibility='onchange'),
        'sequence': fields.integer(
            'Sequence', track_visibility='onchange', group_operator='min'),

        'postal_coordinate_ids':
            fields.one2many(
                'postal.coordinate', 'address_id', string='Postal Coordinates',
                domain=[('active', '=', True)],
                context={'force_recompute': True}),
        'postal_coordinate_inactive_ids':
            fields.one2many(
                'postal.coordinate', 'address_id', string='Postal Coordinates',
                domain=[('active', '=', False)]),
    }

    _defaults = {
        'country_id': lambda self, cr, uid, c:
            self.pool.get('res.country')._country_default_get(
                cr, uid, COUNTRY_CODE, context=c),
        'country_code': COUNTRY_CODE,
        'sequence': 0,
    }

    _order = 'country_id, zip, name'

# constraints

    _unicity_keys = 'technical_name, sequence'

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Increase sequence value when duplicating address
        """
        adr_id = isinstance(ids, (long, int)) and [ids] or ids
        technical_name = self.read(
            cr, uid, adr_id[0], ['technical_name'],
            context=context)['technical_name']
        cr.execute(
            'SELECT MAX(sequence) FROM %s WHERE technical_name=%%s' % (
                self._table,), (technical_name,))
        sequence = cr.fetchone()
        sequence = sequence and sequence[0] or False
        if not sequence:
            raise orm.except_orm(
                _('Error'),
                _('An Address without sequence number cannot be duplicated!'))

        default = dict(default or {})
        default.update({
            'sequence': sequence + 1,
            'postal_coordinate_ids': [],
            'postal_coordinate_inactive_ids': [],
        })
        res = super(address_address, self).copy_data(
            cr, uid, ids, default=default, context=context)
        return res

# view methods: onchange, button

    def onchange_country_id(self, cr, uid, ids, country_id, context=None):
        return {
            'value': {
                'country_code': self.pool.get('res.country').read(
                    cr, uid, [country_id], ['code'],
                    context=context)[0]['code'] if country_id else False,
                'address_local_zip_id': False,
            }
        }

    def onchange_local_zip_id(self, cr, uid, ids, local_zip_id, context=None):
        _zip, city = False, False
        if local_zip_id:
            zip_city = self.pool.get('address.local.zip').read(
                cr, uid, [local_zip_id], [], context=context)[0]
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

    def onchange_local_street_id(self, cr, uid, ids, local_street_id,
                                 context=None):
        vals = {} if local_street_id else {
            'select_alternative_address_local_street': False}
        vals.update({'street_man': False})
        return {
            'value': vals
        }

# public methods

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        Return all partners ids linked to addresses ids
        :param: ids
        :type: list of addresses ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        coord_ids = self._get_linked_coordinates(cr, uid, ids, context=context)
        return self.pool['postal.coordinate'].get_linked_partners(
            cr, uid, coord_ids, context=context)


class postal_coordinate(orm.Model):

    _name = 'postal.coordinate'
    _inherit = ['abstract.coordinate']
    _description = 'Postal Coordinate'

    _track = {
        'bounce_counter': {
            'mozaik_address.address_failure_notification':
                lambda self, cr, uid, obj, ctx=None: obj.bounce_counter,
        },
    }

    _discriminant_field = 'address_id'
    _trigger_fields = []
    _undo_redirect_action = 'mozaik_address.postal_coordinate_action'

    _columns = {
        'address_id':
            fields.many2one(
                'address.address', string='Address', required=True,
                readonly=True, select=True),
        'co_residency_id':
            fields.many2one('co.residency', string='Co-Residency', select=True)
    }

    _rec_name = _discriminant_field

# constraints

    _unicity_keys = 'partner_id, %s' % _discriminant_field

# view methods: onchange, button

    def onchange_unauthorized(
            self, cr, uid, ids, unauthorized, co_residency_id, context=None):
        if unauthorized and co_residency_id:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _(
                        'Unauthorizing a coordinate usually involves '
                        'a change in its co-residency.'
                    )
                }
            }

# public methods

    def name_get(self, cr, uid, ids, context=None):
        result = super(postal_coordinate, self).name_get(
            cr, uid, ids, context=context)
        new_result = []
        for res in result:
            data = self.read(cr, uid, res[0], ['co_residency_id'],
                             context=context)
            name = res[1]
            if data['co_residency_id']:
                name = "%s (%s)" % (name, data['co_residency_id'][1])
            new_result.append((res[0], name))
        return new_result

    def get_fields_to_update(self, cr, uid, mode, context=None):
        """
        :type mode: char
        :param mode: mode defining return values
        :rtype: dictionary
        :rparam: values to update
        """
        res = super(postal_coordinate, self).get_fields_to_update(
            cr, uid, mode, context=context)
        if mode in ['duplicate', 'reset']:
            res.update({'co_residency_id': False})
        return res


class co_residency(orm.Model):

    _name = 'co.residency'
    _inherit = ['mozaik.abstract.model']
    _description = 'Co-Residency'

    _inactive_cascade = True

    _columns = {
        'address_id': fields.many2one(
            'address.address', string='Address',
            required=True, readonly=True, select=True),
        'line': fields.char('Line 1', track_visibility='onchange'),
        'line2': fields.char('Line 2', track_visibility='onchange'),

        'postal_coordinate_ids': fields.one2many(
            'postal.coordinate', 'co_residency_id',
            string='Postal Coordinates'),
    }

    _rec_name = 'address_id'

# constraints

    _unicity_keys = 'address_id'

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        :rparam: list of (id, name)
                 where id is the id of each object
                 and name, the name to display.
        :rtype: [(id, name)] list of tuple
        """
        if not ids:
            return []

        context = context or self.pool['res.users'].context_get(cr, uid)

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for record in self.read(cr, uid, ids, ['line', 'line2'],
                                context=context):
            if not record['line'] and not record['line2']:
                name = _("Co-Residency to complete")
            else:
                name = "/".join([line for line in
                                 [record['line'], record['line2']] if line])
            res.append((record['id'], name))
        return res

    def unlink(self, cr, uid, ids, context=None):
        '''
        Force "undo allow duplicate" when deleting a co-residency
        '''
        ids = isinstance(ids, (long, int)) and [ids] or ids
        coords = self.read(
            cr, uid, ids, ['postal_coordinate_ids'], context=context)
        cids = []
        for c in coords:
            cids += c['postal_coordinate_ids']
        if cids:
            self.pool['postal.coordinate'].button_undo_allow_duplicate(
                cr, uid, cids, context=context)
        res = super(co_residency, self).unlink(cr, uid, ids, context=context)
        return res
