# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class IntInstance(models.Model):
    _inherit = 'int.instance'

    product_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        help="Price list containing prices to apply for your subscriptions",
        copy=False,
    )

    @api.multi
    @api.constrains('product_pricelist_id')
    def _check_number_int_instance(self):
        """
        Odoo constrain to ensure a price list is only used into 1 instance.
        Call the function define on the product.pricelist
        (Done on price list to have a easy check)
        :return:
        """
        self.mapped("product_pricelist_id")._check_number_int_instance()
