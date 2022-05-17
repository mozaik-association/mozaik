# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class ResPartner(models.Model):

    _inherit = "res.partner"

    journal_item_count = fields.Integer(
        groups="account.group_account_invoice,account.group_account_readonly"
    )

    @api.depends(
        "stored_reference",
        "membership_line_ids",
        "membership_line_ids.reference",
        "membership_line_ids.paid",
    )
    def _compute_reference(self):
        return super(ResPartner, self)._compute_reference()

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

    def pay_membership(self, amount_paid, move_id, bank_account_id):
        # TODO what's the default behavior without membership request?
        pass

    def action_account_moves_from_partner(self):
        action = self.sudo().env.ref("account.action_account_moves_all").read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        return action
