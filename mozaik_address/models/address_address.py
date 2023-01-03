# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.mozaik_tools.tools import format_value


class AddressAddress(models.Model):

    _name = "address.address"
    _inherit = ["mozaik.abstract.model"]
    _description = "Address"
    _order = "country_id, zip, name"

    _unicity_keys = "technical_name, sequence"

    name = fields.Char(
        compute="_compute_integral_address",
        string="Address",
        index=True,
        store=True,
    )
    technical_name = fields.Char(
        compute="_compute_integral_address", index=True, store=True
    )
    country_id = fields.Many2one(
        "res.country",
        "Country",
        required=True,
        index=True,
        tracking=True,
        default=lambda s: s._default_country_id(),
    )
    enforce_cities = fields.Boolean(related="country_id.enforce_cities", readonly=True)
    country_code = fields.Char(related="country_id.code", readonly=True)
    zip = fields.Char(compute="_compute_zip", store=True)
    city_id = fields.Many2one(
        "res.city",
        string="City (Rel)",
        tracking=True,
    )
    zip_man = fields.Char(string="Zip (Text)", tracking=True)
    city = fields.Char(compute="_compute_zip", store=True)
    city_man = fields.Char(
        string="City (Text)",
        tracking=True,
    )
    street = fields.Char(compute="_compute_street", store=True)
    street_man = fields.Char("Street (Text)", tracking=True)
    street2 = fields.Char(
        tracking=True,
    )
    number = fields.Char(
        tracking=True,
    )
    box = fields.Char(
        tracking=True,
    )
    sequence = fields.Integer(tracking=True, default=0, group_operator="min")
    partner_ids = fields.One2many(
        "res.partner",
        "address_address_id",
        string="Partners",
        domain=[("active", "=", True)],
        context={"force_recompute": True},
    )
    partner_inactive_ids = fields.One2many(
        "res.partner",
        "address_address_id",
        string="Partners (inactive)",
        domain=[("active", "=", False)],
    )
    has_street = fields.Boolean(
        compute="_compute_has_street", search="_search_has_street"
    )

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
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("default.country.code", default="BE")
        )

    @api.model
    def _default_country_id(self):
        return self.env["res.country"]._country_default_get(
            self._get_default_country_code()
        )

    @api.depends(
        "zip_man",
        "city_man",
        "city_id",
        "city_id.name",
        "city_id.zipcode",
    )
    def _compute_zip(self):
        for adrs in self:
            adrs.zip = adrs.city_id and adrs.city_id.zipcode or adrs.zip_man or False
            adrs.city = adrs.city_id and adrs.city_id.name or adrs.city_man or False

    @api.depends(
        "box",
        "number",
        "street_man",
    )
    def _compute_street(self):
        for adrs in self:
            number = adrs.number or adrs.box and "-" or False
            number = "/".join([el for el in [number, adrs.box] if el])
            street = adrs.street_man or False
            adrs.street = " ".join([el for el in [street, number] if el])

    @api.depends(
        "zip",
        "box",
        "city",
        "street",
        "number",
        "zip_man",
        "city_man",
        "sequence",
        "street_man",
        "city_id",
        "country_id",
        "country_id.name",
    )
    def _compute_integral_address(self):
        country_code = self._get_default_country_code()
        for adrs in self:
            elts = [
                adrs.street or False,
                adrs.sequence and "[%s]" % adrs.sequence or False,
                adrs.street and "-" or adrs.sequence and "-" or False,
                (adrs.country_code == country_code) and adrs.zip or False,
                adrs.city or False,
                (adrs.country_code != country_code) and "-" or False,
                (adrs.country_code != country_code) and adrs.country_id.name or False,
            ]
            adr = " ".join([el for el in elts if el])

            key_fields = self._get_key_field()
            values = key_fields.copy()
            for field in key_fields:
                to_evaluate = (
                    field
                    if not key_fields[field]
                    else "%s.%s" % (field, key_fields[field])
                )
                field_value = adrs.mapped(to_evaluate)
                real_value = field_value[0] if field_value else False
                values[field] = real_value
            technical_name = self._get_technical_name(values)

            adrs.name = adr or False
            adrs.technical_name = technical_name or False

    @api.model
    def _get_key_field(self):
        return OrderedDict(
            [
                ("country_id", "id"),
                ("city_id", "id"),
                ("zip_man", False),
                ("city_man", False),
                ("street_man", False),
                ("number", False),
                ("box", False),
            ]
        )

    @api.onchange("country_id")
    def _onchange_country_id(self):
        for record in self:
            record.city_id = False

    @api.onchange("city_id")
    def _onchange_city_id(self):
        for record in self:
            record.zip = record.city_id.zipcode
            record.city = record.city_id.name
            record.zip_man = False
            record.city_man = False

    def copy_data(self, default=None):
        """
        Increase sequence value when duplicating address
        """
        self.ensure_one()
        cr = self.env.cr
        cr.execute(
            "SELECT MAX(sequence) FROM address_address " "WHERE technical_name=%s",
            (self.technical_name,),
        )
        sequence = cr.fetchone()
        sequence = sequence[0] if sequence else False
        if sequence is False:
            raise ValidationError(
                _("An Address without sequence number cannot be duplicated!")
            )

        default = dict(default or {})
        default.update(
            {
                "sequence": sequence + 1,
            }
        )
        res = super().copy_data(default=default)
        return res

    @api.model
    def _get_technical_name(self, values):
        """
        This method produces a technical name with the content of values.
        :type values: dictionary
        :param values: used to create a technical address name
            ``country_id``
            ``city_id``
            ``zip_man``
            ``city_man``
            ``street_man``
            ``number``
            ``box``
        :rparam: formated values of ``values`` join wit a `#`.
                0 if value is null
        """
        technical_value = []
        for field in values:
            value = values[field] or "0"
            technical_value.append(format_value(value))
        return "#".join(technical_value)

    @api.depends("street_man", "street2")
    def _compute_has_street(self):
        for address in self:
            address.has_street = address.street_man or address.street2

    @api.model
    def _get_partial_address_domain(self):
        return [("street_man", "=", False), ("street2", "=", False)]

    def _search_has_street(self, operator, value):
        """
        Cases supported are
        * operator in ['=', '!=']
        * value is a boolean
        """
        if operator not in [
            "=",
            "!=",
        ] or not isinstance(value, bool):
            raise ValueError(_("This operator/value is not supported"))
        if operator == "!=":
            value = not value
        partial_addresses = self.env["address.address"].search(
            self._get_partial_address_domain()
        )
        if value:
            return [("id", "not in", partial_addresses.ids)]
        return [("id", "in", partial_addresses.ids)]
