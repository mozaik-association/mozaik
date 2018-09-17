# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class MembershipLine(models.Model):
    _inherit = 'membership.line'

    @api.model
    def _get_subscription_price(self, product, partner=False, instance=False):
        """
        Get the subscription price based on given product.
        Inherit to use pricelist to have the price
        :param product: product.product recordset
        :param partner: res.partner recordset
        :param int.instance: int.instance recordset
        :return: float
        """
        if not instance:
            instance = self.env['int.instance'].browse()
        if not partner:
            partner = self.env['res.partner'].browse()
        if instance.product_pricelist_id:
            product = product.with_context(
                pricelist=instance.product_pricelist_id.id,
                partner=partner.id,
            )
        return super(MembershipLine, self)._get_subscription_price(
            product=product, partner=partner, instance=instance)
