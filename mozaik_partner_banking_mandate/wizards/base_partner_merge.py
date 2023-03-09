# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class MergePartnerAutomatic(models.TransientModel):
    _inherit = "base.partner.merge.automatic.wizard"

    def _merge(self, partner_ids, dst_partner=None, extra_checks=True):
        """
        Re-compute 'has_valid_mandate' after merge
        """
        res = super()._merge(partner_ids, dst_partner, extra_checks)
        dst_partner._compute_has_valid_mandate()
        return res
