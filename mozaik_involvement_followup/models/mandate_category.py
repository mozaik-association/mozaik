# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MandateCategory(models.Model):

    _inherit = "mandate.category"

    def _get_active_representative(self, instance_id, users_only):
        """
        Search for active representatives of a given mandate category
        for a given internal instance
        """
        self.ensure_one()
        instances = self.env["int.instance"]
        mandates = self.int_mandate_ids
        if users_only:
            mandates = mandates.filtered(lambda s: s.partner_id.user_ids)
        assemblies = mandates.mapped("int_assembly_id")
        for instance in assemblies.mapped("instance_id"):
            iis = instance.search([("id", "child_of", instance.id)])
            if instance_id in iis._ids:
                instances |= instance
        mandates = mandates.filtered(
            lambda s: s.int_assembly_id.instance_id in instances
        )
        res = mandates.mapped("partner_id")
        return res.ids
