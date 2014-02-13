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

from openerp.osv import orm, fields
from openerp.tools.translate import _

from openerp.addons.ficep_base.controller.main import Controller as Ctrl


"""
Available Type for 'phone.phone':
Mobile Phone - Phone - Fax
"""
AVAILABLE_TYPE = [('mobile', 'Mobile'),
                  ('fix', 'Fix'),
                  ('fax', 'Fax')]

PREFIX_CODE = 'BE'


class phone_phone(orm.Model):

    _name = 'phone.phone'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

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
                'name': fields.char('Number', required=True, size=50),
                'type': fields.selection(AVAILABLE_TYPE, 'Type', required=True),
                'phone_coordinate_ids': fields.one2many('phone.coordinate', 'phone_id', 'Phone Coordinate'),
                }

    _sql_constraints = [
             ('check_unicity_number', 'unique(name)', _('This Phone already exists!'))
     ]

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


class phone_coordinate(orm.Model):

    _name = 'phone.coordinate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'phone_id'

    def get_target_domain(self, phone_type, partner_id):
        """
        =================
        get_target_domain
        =================
        :parma phone_type: the type of the phone
        :type phone_type: char
        :param partner_id: id of the partner
        :type partner_id: integer
        :rparam: dictionary with ``phone_type`` and ``partner_id`` well set
        :rtype: dictionary
        """
        return [('phone_type', '=', phone_type),
                 ('is_main', '=', True),
                 ('active', '=', True),
                 ('partner_id', '=', partner_id)]

    def get_fields_to_update(self, context=None):
        context = context or {}
        return {'active': False, 'expire_date': fields.date.today()} if context.get('invalidate', False) else {'is_main': False}

    def invalidate(self, cr, uid, ids, context=None):
        """
        ==========
        invalidate
        ==========
        This method will invalidate the phone.coordinate by setting
        * active to False
        * expire_date to current date
        :rparam: True
        :rtype: boolean
        **Note**
        Launched from the button 'invalidate'
        """
        context = context or {}
        return super(phone_coordinate, self).write(cr, uid, ids,
                                            {'active': False, 'expire_date': fields.date.today()},
                                            context=context)

    def select_as_main(self, cr, uid, ids, context=None):
        """
        ==============
        select_as_main
        ==============
        This method allows to switch main coordinate:
        1) Check And Set Existing main coordinate for the partner to 'active' = False
        2) Replace the old reference value into the res_partner by current coordinate
        3) Set is_main to True for current coordinate
        :rparam: True
        :rtype: boolean
        """
        context = context or {}
        rec_phone_coordinate = self.browse(cr, uid, ids, context=context)[0]

        target_domain = self.get_target_domain(rec_phone_coordinate.phone_type, rec_phone_coordinate.partner_id.id)
        target_model = self._name
        fields_to_update = self.get_fields_to_update(context)
        model_field = 'fix_coordinate_id' if self.read(cr, uid, ids, \
                      ['phone_type'], context=context) == 'fix' else 'mobile_coordinate_id'

        ctrl = Ctrl(cr, uid, context)
        ctrl.check_unicity_main(self, target_model, target_domain, fields_to_update)
        ctrl.replicate(self, ids[0], model_field)

        return super(phone_coordinate, self).write(cr, uid, ids, {'is_main': True}, context=context)

    def redirect_from_select_as_main(self, cr, uid, vals, context=None):
        """
        ============================
        redirect_from_select_as_main
        ============================
        Two possible case:
        1) A phone coordinate with partner_id,phone_id and no expire_date already
            exists => if it is not a main, set it otherwise do nothing
        2) If there is no phone coordinate then create passing ``vals``
        """
        context = context or {}
        res_ids = self.search(cr, uid, [('partner_id', '=', vals['partner_id']),
                                        ('phone_id', '=', vals['phone_id']),
                                        ('expire_date', '=', False)], context=context)
        if len(res_ids) == 0:
            # must be create
            self.create(cr, uid, vals, context=context)
        else:
            # If the found record  is not ``main``: set it by calling ``select_as_main``
            if not self.read(cr, uid, res_ids[0], ['is_main'], context=context)['is_main']:
                self.select_as_main(cr, uid, res_ids, context=context)

    def check_at_least_one_main(self, cr, uid, ids, context=None):
        """
        =======================
        check_at_least_one_main
        =======================
        That constraint will check the associated partner has at least one main
        coordinate if this current one isn't it
        :rparam: True if The associated partner has already a main coordinate
                 Otherwise False
        :rtype: boolean
        """
        context = context or {}
        phone_coordinate = self.browse(cr, uid, ids, context=context)[0]
        if phone_coordinate.phone_type == 'phone':
            if not phone_coordinate.partner_id.fix_coordinate_id and not phone_coordinate.is_main:
                return False
        else:
            if not phone_coordinate.partner_id.mobile_coordinate_id and not phone_coordinate.is_main:
                return False
        return True

    def check_unicity(self, cr, uid, ids, context=None):
        """
        =============
        check_unicity
        =============
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

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'phone_id': fields.many2one('phone.phone', string='Phone', required=True, readonly=True),
        'active': fields.boolean('Active', readonly=True),
        'vip': fields.boolean('VIP'),
        'unauthorized': fields.boolean('Unauthorized'),
        'is_main': fields.boolean('Is Main', readonly=True),
        'phone_type': fields.related('phone_id', 'type', type='selection', string='Phone Type',
                                      relation='phone.phone', selection=AVAILABLE_TYPE, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Contact', readonly=True, required=True,),
        'coordinate_category_id': fields.many2one('coordinate.category', 'Coordinate Category'),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', readonly=True),
    }

    _defaults = {
        'active': True
    }

    _constraints = [
        (check_at_least_one_main, _('Error! At least one main coordinate by associated partner'), ['partner_id']),
        (check_unicity, _('This Phone Coordinate already exists for this contact'), ['phone_id', 'partner_id', 'expire_date'])
    ]

    def create(self, cr, uid, vals, context=None):
        """
        =======================
        create phone.coordinate
        =======================
        When 'is_main' is true the coordinate has to become the main coordinate for its
        associated partner.
        That implies to remove the current-valid-main coordinate by calling the
        ``check_unicity_main()`` of Controller.
        Next step is to replicate (ref. spec.) the new coordinate into the related partner
        In the end call super create
        :rparam: id of the new phone coordinate
        :rtype: integer
        """
        context = context or {}
        if vals.get('is_main', False):
            ctrl = Ctrl(cr, uid, context)
            phone_type = vals.get('phone_type', False) or self.pool.get('phone.phone').read(cr, uid, vals['phone_id'], ['type'], context=context)['type']
            target_domain = self.get_target_domain(phone_type, vals['partner_id'])
            target_model = self._name
            fields_to_update = self.get_fields_to_update(context)
            ctrl.check_unicity_main(self, target_model, target_domain, fields_to_update)
            new_id = super(phone_coordinate, self).create(cr, uid, vals, context=context)
            model_field = 'fix_coordinate_id' if phone_type == 'fix' else 'mobile_coordinate_id'
            ctrl.replicate(self, new_id, model_field)
            return new_id
        return super(phone_coordinate, self).create(cr, uid, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
