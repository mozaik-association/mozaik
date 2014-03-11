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
import phonenumbers as pn

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


"""
Available Types for 'phone.phone':
Fix - Mobile - Fax
"""
PHONE_AVAILABLE_TYPES = [
    ('fix', 'Fix'),
    ('mobile', 'Mobile'),
    ('fax', 'Fax'),
]

phone_available_types = dict(PHONE_AVAILABLE_TYPES)

PREFIX_CODE = 'BE'


class phone_phone(orm.Model):

    _name = 'phone.phone'
    _description = "Phone Number"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _check_and_format_number(self, cr, uid, num, context=None):
        """
        ========================
        _check_and_format_number
        ========================
        :param vals: containing at least 'name' that is the phone number
        :type vals: dictionary
        :returns: Number formated into a International Number
                  If number is not starting by '+' then check if it starts by '00'
                  and replace it with '+'. Otherwise set a code value with a PREFIX
        :rtype: char
        :raise: pn.NumberParseException
                * if number is not parsing due to a bad encoded value
        """
        code = False
        if num[:2] == '00':
            num = '%s%s' % (num[:2].replace('00', '+'), num[2:])
        elif not num.startswith('+'):
            code = self.get_default_country_code(cr, uid, context=context)
        try:
            normalized_number = pn.parse(num, code) if code else pn.parse(num)
        except pn.NumberParseException, e:
            raise orm.except_orm(_('Warning!'), _('Invalid phone number: %s') % _(e))
        return pn.format_number(normalized_number, pn.PhoneNumberFormat.INTERNATIONAL)

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Number', size=50, required=True, select=True, track_visibility='onchange'),
        'type': fields.selection(PHONE_AVAILABLE_TYPES, 'Type', required=True, track_visibility='onchange'),
        'phone_coordinate_ids': fields.one2many('phone.coordinate', 'phone_id', 'Phone Coordinate'),
    }

    _order = "name"

    _defaults = {
        'type': PHONE_AVAILABLE_TYPES[0],
    }

    _sql_constraints = [
        ('check_unicity_number', 'unique(name)', _('This phone number already exists!'))
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
        for record in self.read(cr, uid, ids, ['name', 'type'], context=context):
            display_name = "%s (%s)" % (record['name'], phone_available_types.get(record['type']))
            res.append((record['id'], display_name))
        return res

    def create(self, cr, uid, vals, context=None):
        """
        ==================
        create phone.phone
        ==================
        This method will create a phone number after checking and format this
        Number, calling the _check_and_format_number method
        :param: vals
        :type: dictionary that contains at least 'name'
        :rparam: id of the new phone
        :rtype: integer
        """
        vals['name'] = self._check_and_format_number(cr, uid, vals['name'], context=context)
        return super(phone_phone, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        ==================
        write phone.phone
        ==================
        This method will update a phone number after checking and format this
        Number, calling the _check_and_format_number method
        :param: vals
        :type: dictionary that possibly contains 'name'
        :rparam: True
        :rtype: boolean
        """
        num = vals.get('name', False)
        if num:
            vals['name'] = self._check_and_format_number(cr, uid, num, context=context)
        return super(phone_phone, self).write(cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, ids, default=None, context=None):
        raise orm.except_orm(_('Error'), _('A phone number cannot be duplicated!'))

# public methods

    def get_default_country_code(self, cr, uid, context=None):
        """
        ========================
        get_default_country_code
        ========================
        This method will return a country code.
        e.g. BE, FR, ...
        The country code firstly will be the value of the parameter key ``default.country.code.phone``
        If no value then take the default country code PREFIX_CODE
        :rparam: Country code found into the config_parameter or PREFIX_CODE
        :rtype: char
        """
        param_id = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'default.country.code.phone')], context=context)
        if param_id:
            return self.pool.get('ir.config_parameter').read(cr, uid, param_id, ['value'], context=context)[0]['value']
        return PREFIX_CODE

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Return partner ids linked to all related coordinate linked to phone ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        phone_rds = self.browse(cr, uid, ids, context=context)
        partner_ids = []
        for record in phone_rds:
            for associated_coordinate in record.phone_coordinate_ids:
                partner_ids.append(associated_coordinate.partner_id.id)
        return partner_ids

    def get_linked_phone_coordinates(self, cr, uid, ids, context=None):
        """
        ============================
        get_linked_phone_coordinates
        ============================
        Return phone coordinate ids linked to phone ids
        :rparam: phone_coordinate_ids
        :rtype: list of ids
        """
        phones = self.read(cr, uid, ids, ['phone_coordinate_ids'], context=context)
        res_ids = []
        for phone in phones:
            res_ids += phone['phone_coordinate_ids']
        return list(set(res_ids))


class phone_coordinate(orm.Model):

    _name = 'phone.coordinate'
    _inherit = ['abstract.coordinate']
    _description = "Phone Coordinate"

    _discriminant_field = 'phone_id'
    _undo_redirect_action = 'ficep_phone.phone_coordinate_action'

    _columns = {
        'phone_id': fields.many2one('phone.phone', string='Phone', required=True, readonly=True, select=True),

        'coordinate_type': fields.related('phone_id', 'type', string='Phone Type', readonly=True,
                                          type='selection', selection=PHONE_AVAILABLE_TYPES,
                                          store={
                                             'phone.coordinate': (lambda self, cr, uid, ids, context=None: ids, ['phone_id'], 10),
                                             'phone.phone': (phone_phone.get_linked_phone_coordinates, ['type'], 10),
                                          },
                                         ),
    }

    _defaults = {
        'coordinate_type': False,
    }

# orm methods

    def create(self, cr, uid, vals, context=None):
        """
        ======
        create
        ======
        When 'is_main' is true the coordinate has to become the main coordinate for its
        associated partner.
        :rparam: id of the new coordinate
        :rtype: integer
        """
        vals['coordinate_type'] = self.pool.get('phone.phone').read(cr, uid, vals['phone_id'], ['type'], context=context)['type']
        return super(phone_coordinate, self).create(cr, uid, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
