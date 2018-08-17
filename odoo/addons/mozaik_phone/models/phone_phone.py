# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, exceptions, fields, models, _

_logger = logging.getLogger(__name__)

try:
    import phonenumbers as pn
except (ImportError, IOError) as err:
    _logger.debug(err)


class PhonePhone(models.Model):
    _name = 'phone.phone'
    _inherit = ['mozaik.abstract.model']
    _description = 'Phone Number'
    _order = 'name'
    _unicity_keys = 'name'

    name = fields.Char(
        'Number',
        required=True,
        index=True,
        track_visibility='onchange',
    )
    type = fields.Selection(
        [
            ('fix', 'Fix'),
            ('mobile', 'Mobile'),
            ('fax', 'Fax'),
        ],
        required=True,
        track_visibility='onchange',
    )
    also_for_fax = fields.Boolean(
        'Also for Fax',
        default=False,
        track_visibility='onchange',
    )
    phone_coordinate_ids = fields.One2many(
        'phone.coordinate',
        'phone_id',
        'Phone Coordinates',
        domain=[('active', '=', True)],
        context={'force_recompute': True},
    )
    phone_coordinate_inactive_ids = fields.One2many(
        'phone.coordinate',
        'phone_id',
        'Phone Coordinates',
        domain=[('active', '=', False)],
    )

    @api.model
    def _update_values(self, vals, mode='write'):
        if 'type' in vals and vals.get('type') != 'fix':
            vals.update(also_for_fax=False)
        if 'name' in vals:
            vals.update({
                'name': self._check_and_format_number(vals.get('name')),
            })

    @api.model
    def _check_and_format_number(self, num):
        """
        Number formatted into a International Number
        If number is not starting by '+' then check if it starts by
        '00'
        and replace it with '+'. Otherwise set a code value with
        a PREFIX
        :param num: str
        :return: str
        """
        code = False
        numero = num
        if num[:2] == '00':
            numero = '%s%s' % (num[:2].replace('00', '+'), num[2:])
        elif not num.startswith('+'):
            code = self._get_default_country_code()
        try:
            normalized_number = pn.parse(
                numero, code) if code else pn.parse(numero)
        except pn.NumberParseException as e:
            errmsg = _('Invalid phone number: %s') % e
            raise exceptions.UserError(errmsg)
        return pn.format_number(
            normalized_number,
            pn.PhoneNumberFormat.INTERNATIONAL)

    @api.multi
    def name_get(self):
        """

        :return: list of tuple
        """
        fld_type = dict(self._fields.get('type').selection)
        res = []
        for record in self:
            phone_type = _('Fix + Fax') if record.also_for_fax else \
                fld_type.get(record.type, '?')
            display_name = "%s (%s)" % (record.name, phone_type)
            res.append((record.id, display_name))
        return res

    @api.model
    def create(self, vals):
        """
        This method will create a phone number after checking and format this
        Number, calling the _check_and_format_number method
        :param vals: dict
        :return: self recordset
        """
        self._update_values(vals, mode='create')
        return super().create(vals)

    @api.multi
    def write(self, vals):
        """
        Update data and update the record
        :param vals: dict
        :return: bool
        """
        self._update_values(vals)
        return super().write(vals)

    @api.multi
    def copy(self, default=None):
        """
        Raise an exception to have a better error message.
        Because a phone number can not be duplicated
        :param default: dict
        """
        # pylint: disable=method-required-super
        raise exceptions.ValidationError(
            _("A phone number cannot be duplicated!"))

    @api.model
    def _get_default_country_code(self):
        """
        This method will return a country code.
        e.g. BE, FR, ...
        The country code firstly will be the value of the parameter key
        ``default.country.code``
        If no value then take the default country code 'BE'
        :return: str
        """
        return self.env['ir.config_parameter'].get_param(
            "default.country.code", default='BE')

    @api.multi
    @api.onchange('type')
    def onchange_type(self):
        for phone in self:
            phone.also_for_fax = False
