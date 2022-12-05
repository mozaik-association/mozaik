# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartnerBank(models.Model):

    _inherit = "res.partner.bank"

    def write(self, vals):
        if "partner_id" in vals:
            old_partners = self.mapped("partner_id")
            res = super().write(vals)
            new_partners = self.mapped("partner_id")
            (old_partners | new_partners)._compute_has_valid_mandate()
            return res
        return super().write(vals)
