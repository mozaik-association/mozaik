# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models, _
from odoo.exceptions import except_orm

_logger = logging.getLogger(__name__)

try:
    import phonenumbers as pn
except (ImportError, IOError) as err:
    _logger.debug(err)

PHONE_AVAILABLE_TYPES = [
    ('fix', 'Fix'),
    ('mobile', 'Mobile'),
    ('fax', 'Fax'),
]

phone_available_types = dict(PHONE_AVAILABLE_TYPES)

PREFIX_CODE = 'BE'


class PhonePhone(models.Model):

    _name = 'phone.phone'
    _inherit = ['mozaik.abstract.model']
    _description = 'Phone Number'

    @api.multi
    def _get_linked_coordinates(self):
        return self.env['phone.coordinate'].search(
            [('phone_id', 'in', self.ids)])

    @api.model
    def _validate_data(self, vals, mode='write'):
        if 'type' in vals and vals['type'] != PHONE_AVAILABLE_TYPES[0][0]:
            vals.update(also_for_fax=False)
        if 'name' in vals:
            vals['name'] = self._check_and_format_number(vals['name'])

    @api.model
    def _check_and_format_number(self, num):
        """
        ========================
        _check_and_format_number
        ========================
        :param num: the phone number
        :type num: char
        :returns: Number formated into a International Number
                  If number is not starting by '+' then check if it starts by
                  '00'
                  and replace it with '+'. Otherwise set a code value with
                  a PREFIX
        :rtype: char
        :raise: pn.NumberParseException
                * if number is not parsing due to a bad encoded value
        """
        if self.env.context.get('install_mode', False) and num[:4] == 'tbc ':
            # during data migration suspect number are not checked
            return num
        code = False
        numero = num
        if num[:2] == '00':
            numero = '%s%s' % (num[:2].replace('00', '+'), num[2:])
        elif not num.startswith('+'):
            code = self.get_default_country_code()
        try:
            normalized_number = pn.parse(
                numero,
                code) if code else pn.parse(numero)
        except pn.NumberParseException as e:
            errmsg = _('Invalid phone number: %s') % e
            if self.env.get('install_mode', False):
                # during data migration exception are not allowed
                _logger.warning(errmsg)
                return num
            raise except_orm(_('Error'), errmsg)
        return pn.format_number(
            normalized_number,
            pn.PhoneNumberFormat.INTERNATIONAL)

    name = fields.Char(
        'Number',
        size=50,
        required=True,
        index=True,
        track_visibility='onchange')
    type = fields.Selection(
        PHONE_AVAILABLE_TYPES,
        'Type',
        required=True,
        track_visibility='onchange')
    also_for_fax = fields.Boolean(
        'Also for Fax',
        default=False,
        track_visibility='onchange')
    phone_coordinate_ids = fields.One2many(
        'phone.coordinate',
        'phone_id',
        'Phone Coordinates',
        domain=[('active', '=', True)],
        context={'force_recompute': True})
    phone_coordinate_inactive_ids = fields.One2many(
        'phone.coordinate',
        'phone_id',
        'Phone Coordinates',
        domain=[('active', '=', False)])

    _order = 'name'

# constraints

    _unicity_keys = 'name'

# orm methods

    @api.multi
    def name_get(self):
        """
        ========
        name_get
        ========
        :return: list of tuple (id, name to display)
                 where id is the id of the object into the relation
                 and display_name, the name of this object.
        :rtype: [(id,name)] list of tuple
        """
        fld_type = self.fields_get(['type'])
        fld_type = dict(fld_type['type']['selection'])
        res = []
        for record in self:
            phone_type = record.also_for_fax and _('Fix + Fax') or \
                         fld_type.get(record.type, '?')
            display_name = "%s (%s)" % (record.name, phone_type)
            res.append((record.id, display_name))
        return res

    @api.model
    def create(self, vals):
        """
        ==================
        create phone.phone
        ==================
        This method will create a phone number after checking and format this
        Number, calling the _check_and_format_number method
        :param: vals
        :type: dictionary that contains at least 'name'
        :return: the new phone
        :rtype: phone.phone
        """
        self._validate_data(vals, mode='create')
        return super().create(vals)

    @api.multi
    def write(self, vals):
        """
        =====
        write
        =====
        Validate data and update the record
        :param: vals
        :type: dictionary that possibly contains 'name'
        :return: True
        :rtype: boolean
        """
        self._validate_data(vals)
        return super().write(vals)

    @api.multi
    def copy(self, default=None):
        """
        ================
        copy phone.phone
        ================
        Due to the constraint: to avoid the standard except: better explanation
        for the user
        """
        raise except_orm(
            _('Error'),
            _('A phone number cannot be duplicated!'))

# public methods

    @api.model
    def get_default_country_code(self):
        """
        ========================
        get_default_country_code
        ========================
        This method will return a country code.
        e.g. BE, FR, ...
        The country code firstly will be the value of the parameter key
        ``default.country.code.phone``
        If no value then take the default country code PREFIX_CODE
        :rparam: Country code found into the config_parameter or PREFIX_CODE
        :rtype: char
        """
        param = self.env.get('ir.config_parameter').search(
            [('key', '=', 'default.country.code.phone')])
        if param:
            return param.value
        return PREFIX_CODE

    @api.multi
    def get_linked_partners(self):
        """
        ===================
        get_linked_partners
        ===================
        Return all partners ids linked to phones ids
        :param: ids
        :type: list of addresses ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        coords = self._get_linked_coordinates()
        return self.env['phone.coordinate'].get_linked_partners(coords)

# view methods: onchange, button

    @api.multi
    @api.onchange('type')
    def onchange_type(self):
        for phone in self:
            phone.also_for_fax = False
