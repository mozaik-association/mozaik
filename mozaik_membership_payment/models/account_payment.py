# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPayment(models.Model):

    _inherit = "account.payment"

    @api.depends("journal_id", "partner_id", "partner_type", "is_internal_transfer")
    def _compute_destination_account_id(self):
        res = super(AccountPayment, self)._compute_destination_account_id()
        for ap in self:
            sa = ap.payment_transaction_id.membership_ids.mapped(
                "product_id.property_subscription_account"
            )
            if ap.payment_transaction_id.membership_ids and sa:
                ap.destination_account_id = sa
            else:
                sa = ap.payment_transaction_id.membership_request_ids.mapped(
                    "partner_id.subscription_product_id.property_subscription_account"
                )
                if ap.payment_transaction_id.membership_request_ids and sa:
                    ap.destination_account_id = sa
        return res
