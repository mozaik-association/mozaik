# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = ["product.template"]
    _order = "sequence"

    membership = fields.Boolean("Subscription")
    name = fields.Char(tracking=True)
    list_price = fields.Float(tracking=True)

    @api.model
    def _get_default_subscription(self):
        """
        return the record set of a default membership product
        """
        return self.env.ref("mozaik_membership.membership_product_isolated")
