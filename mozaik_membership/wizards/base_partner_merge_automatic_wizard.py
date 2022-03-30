# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class BasePartnerMergeAutomaticWizard(models.TransientModel):

    _inherit = "base.partner.merge.automatic.wizard"

    def _merge(self, partner_ids, dst_partner=None, extra_checks=True):

        partners = self.env["res.partner"].browse(partner_ids).exists()
        # remove dst_partner from partners to merge
        if dst_partner and dst_partner in partners:
            src_partners = partners - dst_partner
        else:
            ordered_partners = self._get_ordered_partner(partners.ids)
            src_partners = ordered_partners[:-1]

        src_partners.mapped("membership_line_ids")._close(force=True)

        return super(BasePartnerMergeAutomaticWizard, self)._merge(
            partner_ids, dst_partner, extra_checks
        )
