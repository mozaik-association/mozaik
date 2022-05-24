# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.fields import first


class AccountPayment(models.Model):

    _inherit = "account.payment"

    @api.depends("journal_id", "partner_id", "partner_type", "is_internal_transfer")
    def _compute_destination_account_id(self):
        res = super(AccountPayment, self)._compute_destination_account_id()
        for ap in self:
            membership_related = (
                ap.payment_transaction_id.membership_ids
                or ap.payment_transaction_id.membership_request_ids
            )
            if not membership_related:
                continue
            sa = ap.payment_transaction_id.membership_ids.mapped(
                "product_id.property_subscription_account"
            )
            if ap.payment_transaction_id.membership_ids and sa:
                ap.destination_account_id = sa
                continue
            sa = ap.payment_transaction_id.membership_request_ids.mapped(
                "partner_id.subscription_product_id.property_subscription_account"
            )
            if ap.payment_transaction_id.membership_request_ids and sa:
                ap.destination_account_id = sa
                continue
            subscription_accounts = (
                self.env["product.product"]
                .search([("membership", "=", True)])
                .mapped("property_subscription_account")
            )
            ap.destination_account_id = first(subscription_accounts)
        return res

    def _seek_for_lines(self):
        self.ensure_one()
        liquidity_lines, counterpart_lines, writeoff_lines = super(
            AccountPayment, self
        )._seek_for_lines()
        subscription_accounts = (
            self.env["product.product"]
            .search([("membership", "=", True)])
            .mapped("property_subscription_account")
        )
        for line in self.move_id.line_ids:
            if line.account_id in subscription_accounts:
                counterpart_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines
