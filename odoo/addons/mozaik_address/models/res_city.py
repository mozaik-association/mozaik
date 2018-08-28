# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCity(models.Model):

    _name = 'res.city'
    _inherit = ['res.city', 'mozaik.abstract.model']
    _order = "zipcode, sequence, name"
    _unicity_keys = 'zipcode, name, country_id'

    sequence = fields.Integer(default=16)

    # fields redefinition
    zipcode = fields.Char(required=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = "%s %s" % (record.zipcode, record.name)
            result.append((record.id, name))
        return result
