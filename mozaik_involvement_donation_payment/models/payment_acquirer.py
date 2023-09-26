# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    @api.model
    def _get_default_acquirer(self):
        """
        Return the first enabled or test acquirer or Wire Transfer
        """
        enabled_acquirer_id = self.search([("state", "=", "enabled")], limit=1)
        if enabled_acquirer_id:
            return enabled_acquirer_id
        test_acquirer_id = self.search([("state", "=", "test")], limit=1)
        return test_acquirer_id or self.env.ref("payment.payment_acquirer_transfer")
