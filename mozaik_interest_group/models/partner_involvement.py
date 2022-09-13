# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PartnerInvolvement(models.Model):

    _inherit = "partner.involvement"

    def unlink(self):
        """
        Due to security rules, interest groups on the partner are
        computed BEFORE unlink, and aren't recomputed after (Odoo bug).
        We thus force recomputation here.
        """
        partners = self.mapped("partner_id")
        res = super().unlink()
        partners._compute_interest_group_ids()
        return res
