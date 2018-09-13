# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    def _get_membership_prod_info(self, amount, reference):
        self.ensure_one()
        first = self.env.ref('mozaik_membership.membership_product_first')

        if (self.membership_state_code == 'member_candidate' and
                self.reference == reference and
                self.amount == amount):
            return first.id, first.property_subscription_account

        domain = [
            ('membership', '=', True),
            ('list_price', '=', amount),
        ]

        prod_ids = self.env['product.product'].search(domain)
        for prod in prod_ids:
            if prod == first:
                if not (self.membership_state_code == 'member_candidate' and
                        self.reference == reference):
                    continue
            return prod.id, prod.property_subscription_account

        return False, False
