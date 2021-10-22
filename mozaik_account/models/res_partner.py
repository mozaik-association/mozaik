# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _get_membership_prod_info(self, amount, reference):
        """
        Get membership product info
        :param amount: float
        :param reference: str
        :return: tuple: int (product.product id), account.account recordset
        """
        self.ensure_one()
        first = self.env.ref("mozaik_membership.membership_product_first")
        precision = self._fields.get("amount").digits[1]
        # float_compare return 0 is values are equals
        cmp = float_compare(self.amount, amount, precision_digits=precision)
        if (
            self.membership_state_code == "member_candidate"
            and self.reference == reference
            and not cmp
        ):
            return first.id, first.property_subscription_account

        domain = [
            ("membership", "=", True),
            ("list_price", "=", amount),
        ]

        prod_ids = self.env["product.product"].search(domain)
        for prod in prod_ids:
            if prod == first:
                if not (
                    self.membership_state_code == "member_candidate"
                    and self.reference == reference
                ):
                    continue
            return prod.id, prod.property_subscription_account

        return False, False
