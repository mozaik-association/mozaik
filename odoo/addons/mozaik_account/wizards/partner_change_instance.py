# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class PartnerChangeInstance(models.TransientModel):
    """
    Model used to update instances of partner
    """
    _inherit = "partner.change.instance"

    @api.multi
    def _create_new_membership(self, line, product):
        self.ensure_one()
        if line.paid:
            super()._create_new_membership(line, product)
        else:
            price = line._get_subscription_price(
                product, line.partner_id, self.new_instance_id)
            ref = line._generate_membership_reference(
                line.partner_id, self.new_instance_id)
            line.copy({
                'int_instance_id': self.new_instance_id.id,
                'product_id': product.id,
                'price': price,
                'reference': ref,
            })
