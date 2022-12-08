# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankingMandate(models.Model):

    _inherit = "account.banking.mandate"

    @api.model_create_multi
    def create(self, vals_list):
        mandates = super().create(vals_list)
        mandates.mapped("partner_id")._compute_has_valid_mandate()
        return mandates

    def unlink(self):
        partners = self.mapped("partner_id")
        res = super().unlink()
        partners._compute_has_valid_mandate()
        return res

    def write(self, vals):
        if any(f in vals for f in ["partner_id", "partner_bank_id"]):
            old_partners = self.mapped("partner_id")
            res = super().write(vals)
            new_partners = self.mapped("partner_id")
            (old_partners | new_partners)._compute_has_valid_mandate()
            return res
        return super().write(vals)
