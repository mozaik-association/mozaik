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
            dst_partner = ordered_partners[-1]
            src_partners = ordered_partners[:-1]

        # since we close the membership we need to keep an instance for the security
        for p in src_partners:
            p.force_int_instance_id = p.int_instance_id
        dst_force_int_instance_id = dst_partner.force_int_instance_id

        src_partners.mapped("membership_line_ids")._close(force=True)

        res = super(BasePartnerMergeAutomaticWizard, self)._merge(
            partner_ids, dst_partner, extra_checks
        )

        # do not modify the force_int_instance_id since it should be empty if
        # there is a membership_line_id
        dst_partner.force_int_instance_id = dst_force_int_instance_id
        return res
