# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class EmailTemplatePlaceholder(models.Model):
    _inherit = 'email.template.placeholder'

    @api.model
    def _get_default_model(self):
        """
        Get the default model
        :return: ir.model recordset
        """
        return self.env['ir.model'].search(
            [('model', '=', 'email.coordinate')], limit=1)

    model_id = fields.Many2one(
        default=lambda s: s._get_default_model(),
    )
    placeholder = fields.Char(
        default='${object.partner_id.}',
    )
