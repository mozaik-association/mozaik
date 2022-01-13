# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Product(models.Model):

    _inherit = ["product.product"]
    _order = "sequence"

    sequence = fields.Integer(related="product_tmpl_id.sequence", store=True)
