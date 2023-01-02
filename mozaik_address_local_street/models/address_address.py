# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AddressAddress(models.Model):

    _inherit = ["address.address"]

    address_local_street_id = fields.Many2one(
        "address.local.street",
        string="Reference Street",
        tracking=True,
    )
    select_alternative_address_local_street = fields.Boolean(
        "Use Alternative Reference Street",
        tracking=True,
    )

    @api.depends(
        "box",
        "number",
        "street_man",
        "select_alternative_address_local_street",
        "address_local_street_id",
        "address_local_street_id.local_street",
        "address_local_street_id.local_street_alternative",
    )
    def _compute_street(self):
        res = super()._compute_street()
        for adrs in self:
            if adrs.address_local_street_id:
                number = adrs.number or "-"
                number = (
                    adrs.box and "%s/%s" % (number, adrs.box) or adrs.number or False
                )

                street = (
                    adrs.address_local_street_id.local_street_alternative
                    if adrs.select_alternative_address_local_street
                    else adrs.address_local_street_id.local_street
                )
                adrs.street = " ".join([el for el in [street, number] if el])
        return res

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
        "address_local_street_id",
        "country_id",
        "country_id.name",
    )
    def _compute_integral_address(self):
        return super()._compute_integral_address()

    @api.model
    def _get_key_field(self):
        key_fields = super()._get_key_field()
        key_fields.update([("address_local_street_id", "id")])
        # reorder the OrderedDict
        for value in ["street_man", "number", "box"]:
            key_fields.move_to_end(value)
        return key_fields

    @api.onchange("zip")
    def _onchange_zip(self):
        for record in self:
            record.address_local_street_id = False

    @api.onchange("address_local_street_id")
    def _onchange_address_local_street_id(self):
        for record in self:
            if record.address_local_street_id:
                record.street_man = record.address_local_street_id.local_street
                record.select_alternative_address_local_street = False
            record.street_man = False

    @api.depends("street_man", "street2", "address_local_street_id")
    def _compute_has_street(self):
        super()._compute_has_street()
        for address in self.filtered("address_local_street_id"):
            address.has_street = True

    @api.model
    def _get_partial_address_domain(self):
        res = super()._get_partial_address_domain()
        res.append(("address_local_street_id", "=", False))
        return res
