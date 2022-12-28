# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.mozaik_tools.tools import format_value


class ResCity(models.Model):

    _name = "res.city"
    _inherit = ["res.city", "mozaik.abstract.model"]
    _order = "zipcode, sequence, name"
    _unicity_keys = "zipcode, name, country_id"

    sequence = fields.Integer(default=16)
    formatted_name = fields.Char(
        compute="_compute_formatted_name",
        help="City name without space, hyphens and in lower case",
        store=True,
    )

    # fields redefinition
    zipcode = fields.Char(required=True)
    country_id = fields.Many2one(
        default=lambda s: s._default_country_id(),
        domain=[("enforce_cities", "=", True)],
    )

    @api.depends("name")
    def _compute_formatted_name(self):
        for city in self:
            city.formatted_name = format_value(city.name, remove_blanks=True)

    @api.model
    def _default_country_id(self):
        return (
            self.env["address.address"]._default_country_id().filtered("enforce_cities")
        )

    def name_get(self):
        result = []
        for record in self:
            name = "%s %s" % (record.zipcode, record.name)
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if not (name == "" and operator == "ilike"):
            args = list(args or [])
            args += ["|", ("zipcode", operator, name)]
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
