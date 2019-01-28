# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IntMandate(models.Model):

    _inherit = 'int.mandate'

    partner_instance_ids = fields.Many2many(
        related='partner_id.int_instance_ids',
        string='Partner Internal Instance',
    )
    mandate_instance_id = fields.Many2one(
        related='int_assembly_id.instance_id',
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        self.env['ir.rule'].clear_caches()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'partner_id' in vals:
            self.env['ir.rule'].clear_caches()
        return res

    @api.multi
    def unlink(self):
        res = super().unlink()
        self.env['ir.rule'].clear_caches()
        return res
