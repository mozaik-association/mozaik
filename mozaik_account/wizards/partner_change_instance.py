# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class PartnerChangeInstance(models.TransientModel):
    """
    Model used to update instances of partner
    """
    _inherit = "partner.change.instance"

    @api.multi
    def _get_new_membership_values(self):
        self.ensure_one()
        line = self.membership_line_id
        without_ref = (
            line.paid or
            line.state_id.code not in
            line.state_id._get_all_subscription_codes()
        )
        if without_ref:
            this = self.with_context(already_paid=line.paid)
            vals = super(
                PartnerChangeInstance, this)._get_new_membership_values()
        else:
            product = line.partner_id.subscription_product_id
            price = line._get_subscription_price(
                product, line.partner_id, self.new_instance_id)
            ref = line._generate_membership_reference(
                line.partner_id, self.new_instance_id)
            reference, price = line._prepare_custom_renew(ref, price)
            if reference is None:
                reference = ref
            vals = {
                'int_instance_id': self.new_instance_id.id,
                'product_id': product.id,
                'price': price,
                'reference': reference,
            }
        vals['paid'] = line._price_is_zero(vals.get('price', 0.0))
        return vals
