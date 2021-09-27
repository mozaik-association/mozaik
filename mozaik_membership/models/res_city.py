# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class ResCity(models.Model):

    _inherit = 'res.city'

    int_instance_id = fields.Many2one(
        'int.instance', 'Internal Instance', tracking=True,
        default=lambda s: s._default_int_instance_id(), required=True,
        index=True,
        )

    @api.model
    def _default_int_instance_id(self):
        return self.env['int.instance']._get_default_int_instance()
