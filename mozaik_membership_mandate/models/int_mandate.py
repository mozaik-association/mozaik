# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IntMandate(models.Model):

    _inherit = 'int.mandate'

    mandate_instance_id = fields.Many2one(
        related='int_assembly_id.instance_id',
        store='True', index='True', readonly=True,
    )
