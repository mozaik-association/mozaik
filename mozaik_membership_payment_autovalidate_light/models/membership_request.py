# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    def _prepare_vals_for_light_mr(self, matched_partner):
        """
        Copy part of the values of self to create the light MR.
        """
        vals = super()._prepare_vals_for_light_mr(matched_partner)
        vals.update(
            {
                "amount": self.amount,
                "reference": self.reference,
                "auto_validate_after_payment": self.auto_validate_after_payment,
                "transaction_ids": self.transaction_ids,
            }
        )
        # Remove the auto-validate after payment on initial MR
        # because we don't want this one to be auto-validated
        self.auto_validate_after_payment = False
        return vals
