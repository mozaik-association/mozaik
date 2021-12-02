# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ExtMandate(models.Model):

    _inherit = "ext.mandate"

    is_important = fields.Boolean("Important Mandate", index=True, tracking=True)

    @api.onchange("ext_assembly_id")
    def onchange_ext_assembly_id(self):
        res = super().onchange_ext_assembly_id()
        if self.ext_assembly_id:
            self.is_important = self.ext_assembly_id.is_important
        return res

    @api.model
    def create(self, vals):
        if not vals.get("is_important", False):
            assembly_id = vals.get("ext_assembly_id", False)
            assembly = self.env["ext.assembly"].browse(assembly_id)
            if assembly:
                vals["is_important"] = assembly.is_important
        return super().create(vals)
