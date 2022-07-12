# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtAssembly(models.Model):

    _inherit = "ext.assembly"

    def _get_mandates(self):
        """
        return list of mandates linked to the assemblies
        """
        domain = [("ext_assembly_id", "in", self.ids)]
        mandates = self.env["ext.mandate"].search(domain)
        return mandates

    ext_mandate_ids = fields.One2many(
        comodel_name="ext.mandate",
        inverse_name="ext_assembly_id",
        string="External mandates",
        help="External mandates for which the ext assembly is the current record.",
    )
