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

import openerp
from openerp.osv import orm, fields
from openerp.tools.translate import _

from openerp.addons.ficep_base.controller.main import Controller as Ctrl


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

MAIN_COORDINATE_ERROR = _('Exactly one main coordinate must exist for a given partner and a given phone type!')


def _get_field_name_for_type(phone_type):
    """
    ========================
    _get_field_name_for_type
    ========================
    :param phone_type: the type of the phone. must be into the 
           const phone_available_types
    :rparam phone_type: char
    :raise: orm.except_orm if phone_type is not into the constant
        ``phone_available_types``
    """
    if phone_type in phone_available_types:
        field_name = '%s_coordinate_id' % phone_type
    else:
        raise orm.except_orm(_('ValidateError'), _('Invalid phone type: "%s" !') % phone_type or _('Undefined'))
    return field_name


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
        context = context or {}
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
        if context is None:
            context = {}
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
        if context is None:
            context = {}
        num = vals.get('name', False)
        if num:
            vals['name'] = self._check_and_format_number(cr, uid, num, context=context)
        return super(phone_phone, self).write(cr, uid, ids, vals, context=context)

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
        context = context or {}
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

    def get_linked_phone_ccordinates(self, cr, uid, ids, context=None):
        """
        ============================
        get_linked_phone_ccordinates
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
    _description = "Phone Coordinate"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_target_domain(self, partner_id, phone_type):
        """
        ==================
        _get_target_domain
        ==================
        :param partner_id: id of the partner
        :type partner_id: integer
        :parma phone_type: the type of the phone
        :type phone_type: char
        :rparam: dictionary with ``phone_type`` and ``partner_id`` well set
        :rtype: dictionary
        """
        return [('partner_id', '=', partner_id),
                ('phone_type', '=', phone_type),
                ('is_main', '=', True),
               ]

    def _get_fields_to_update(self, context=None):
        context = context or {}
        return {'active': False, 'expire_date': fields.date.today()} if context.get('invalidate', False) else {'is_main': False}

    _columns = {
        'id': fields.integer('ID', readonly=True),

        'partner_id': fields.many2one('res.partner', 'Contact', readonly=True, required=True, select=True),
        'phone_id': fields.many2one('phone.phone', string='Phone', required=True, readonly=True, select=True),
        'coordinate_category_id': fields.many2one('coordinate.category', 'Coordinate Category', select=True, track_visibility='onchange'),

        'is_main': fields.boolean('Is Main', readonly=True, select=True),
        'unauthorized': fields.boolean('Unauthorized', track_visibility='onchange'),
        'vip': fields.boolean('VIP', track_visibility='onchange'),

        'phone_type': fields.related('phone_id', 'type', string='Phone Type', readonly=True,
                                      type='selection', selection=PHONE_AVAILABLE_TYPES,
                                      store={
                                             'phone.coordinate': (lambda self,cr,uid,ids,context=None: ids, ['phone_id'], 10),
                                             'phone.phone': (phone_phone.get_linked_phone_ccordinates, ['type'], 10),
                                            },
                                    ),

        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', readonly=True, track_visibility='onchange'),
        'active': fields.boolean('Active', readonly=True),
    }

    _rec_name = 'phone_id'

    _order = "partner_id, expire_date, is_main desc, phone_type"

    _defaults = {
        'active': True
    }

# constraints

    def _check_one_main_coordinate(self, cr, uid, ids, for_unlink=False, context=None):
        """
        ==========================
        _check_one_main_coordinate
        ==========================
        Check if associated partner has exactly one main coordinate 
        for a given phone type
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        coordinates = self.browse(cr, uid, ids, context=context)
        for coordinate in coordinates:
            if for_unlink and not coordinate.is_main:
                continue
    
            coordinate_ids = self.search(cr, uid, [('partner_id', '=', coordinate.partner_id.id),
                                                   ('phone_type', '=', coordinate.phone_type)], context=context)
    
            if for_unlink and len(coordinate_ids)>1 and coordinate.is_main:
                return False
        
            if not coordinate_ids:
                continue
        
            coordinate_ids = self.search(cr, uid, [('partner_id', '=', coordinate.partner_id.id),
                                                   ('phone_type', '=', coordinate.phone_type),
                                                   ('is_main', '=', True)], context=context)
            if len(coordinate_ids)!=1:
                return False
        
        return True

    def _check_unicity(self, cr, uid, ids, context=None):
        """
        ==============
        _check_unicity
        ==============
        :rparam: False if phone coordinate already exists with (phone_id,partner_id,expire_date)
                 Else True
        :rtype: Boolean
        """
        context = context or {}
        pc_rec = self.browse(cr, uid, ids, context=context)[0]
        res_ids = self.search(cr, uid, [('id', '!=', pc_rec.id),
                                        ('partner_id', '=', pc_rec.partner_id.id),
                                        ('phone_id', '=', pc_rec.phone_id.id),
                                        ('expire_date', '=', False)], context=context)
        return len(res_ids) == 0

    _constraints = [
        (_check_one_main_coordinate, MAIN_COORDINATE_ERROR, ['partner_id']),
        (_check_unicity, _('This phone coordinate already exists for this contact'), ['phone_id', 'partner_id', 'expire_date'])
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
        for record in self.read(cr, uid, ids, ['phone_id'], context=context):
            display_name = record['phone_id'][1]
            res.append((record['id'], display_name))
        return res

    def create(self, cr, uid, vals, context=None):
        """
        =======================
        create phone.coordinate
        =======================
        When 'is_main' is true the coordinate has to become the main coordinate for its
        associated partner.
        That implies to remove the current-valid-main coordinate by calling the
        ``search_and_update()`` of Controller.
        :rparam: id of the new phone coordinate
        :rtype: integer
        """
        vals['phone_type'] = self.pool.get('phone.phone').read(cr, uid, vals['phone_id'], ['type'], context=context)['type']
        coordinate_ids = self.search(cr, uid, [('partner_id', '=', vals['partner_id']),
                                               ('phone_type', '=', vals['phone_type']),
                                               ('is_main', '=', True)], context=context)
        if not coordinate_ids:
            vals['is_main'] = True 
        if vals.get('is_main'):
            ctrl = Ctrl(self, cr, uid)
            target_domain = self._get_target_domain(vals['partner_id'], vals['phone_type'])
            fields_to_update = self._get_fields_to_update(context)
            ctrl.search_and_update(target_domain, fields_to_update, context=context)
            new_id = super(phone_coordinate, self).create(cr, uid, vals, context=context)
        else:
            new_id = super(phone_coordinate, self).create(cr, uid, vals, context=context)
        return new_id

    def unlink(self, cr, uid, ids, context=None):
        """
        =======================
        unlink phone.coordinate
        =======================
        :rparam: True
        :rtype: boolean
        :raise: Error if the coordinate is main
                and another coordinate of the same type exists
        """
        coordinate_ids = self.search(cr, uid, [('id', 'in', ids),('is_main', '=', False)], context=context)
        super(phone_coordinate, self).unlink(cr, uid, coordinate_ids, context=context)
        coordinate_ids = list(set(ids).difference(coordinate_ids))
        if not self._check_one_main_coordinate(cr, uid, coordinate_ids, for_unlink=True, context=context):
            raise orm.except_orm(_('Error!'), MAIN_COORDINATE_ERROR)
        return super(phone_coordinate, self).unlink(cr, uid, coordinate_ids, context=context)

# view methods: onchange, button

    def button_invalidate(self, cr, uid, ids, context=None):
        """
        =================
        button_invalidate
        =================
        This method invalidate a phone.coordinate by setting
        * active to False
        * expire_date to current date
        :rparam: True
        :rtype: boolean
        :raise: Error if the coordinate is main
                and another coordinate of the same type exists
        """
        self.write(cr, uid, ids,
                   {'active': False, 'expire_date': fields.date.today()},
                   context=context)

        return True

# public methods

    def set_as_main(self, cr, uid, ids, context=None):
        """
        ===========
        set_as_main
        ===========
        This method allows to switch main coordinate:
        1) Reset is_main of previous main coordinate
        2) Set is_main of new main coordinate
        :rparam: True
        :rtype: boolean
        """
        rec_phone_coordinate = self.browse(cr, uid, ids, context=context)[0]

        # 1) Reset is_main of previous main coordinate
        ctrl = Ctrl(self, cr, uid)
        target_domain = self._get_target_domain(rec_phone_coordinate.partner_id.id, rec_phone_coordinate.phone_type)
        fields_to_update = self._get_fields_to_update(context)
        ctrl.search_and_update(target_domain, fields_to_update, context=context)

        # 2) Set is_main of new main coordinate
        res=super(phone_coordinate, self).write(cr, uid, ids, {'is_main': True}, context=context)

        return res

    def change_main_phone_number(self, cr, uid, partner_ids, phone_id, context=None):
        """
        ========================
        change_main_phone_number
        ========================
        :param partner_ids: list of partner id
        :type partner_ids: [integer]
        :param phone_id: id of the new main phone.phone
        :type phone_id: integer
        :rparam: list of phone coordinate ids created
        :rtype: list of integer
        """
        return_ids = []
        for partner_id in partner_ids:
            res_ids = self.search(cr, uid, [('partner_id', '=', partner_id),
                                            ('phone_id', '=', phone_id)], context=context)
            if not res_ids:
                # must be create
                return_ids.append(self.create(cr, uid, {'partner_id': partner_id,
                                                        'phone_id': phone_id,
                                                        'is_main': True,
                                                       }, context=context))
            else:
                # If the coordinate is not already ``main``, set it as main
                if not self.read(cr, uid, res_ids[0], ['is_main'], context=context)['is_main']:
                    self.set_as_main(cr, uid, res_ids, context=context)
        return return_ids

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Returns partner ids linked to coordinate ids
        Path to partner must be object.partner_id
        :rparam: partner_ids
        :rtype: list of ids
        """
        model_rds = self.browse(cr, uid, ids, context=context)
        partner_ids = []
        for record in model_rds:
            partner_ids.append(record.partner_id.id)
        return partner_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
