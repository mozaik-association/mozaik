# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    def _stripe_request(self, url, data=False, method="POST"):
        if data and "customer_email" in data and not data["customer_email"]:
            data.pop("customer_email")
        return super(PaymentAcquirer, self)._stripe_request(url, data, method)
