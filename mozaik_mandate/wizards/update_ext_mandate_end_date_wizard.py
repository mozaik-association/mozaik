# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class UpdateExtMandateEndDateWizard(models.TransientModel):

    _inherit = "abstract.update.mandate.end.date.wizard"
    _name = "update.ext.mandate.end.date.wizard"
    _description = "Update Ext Mandate End Date Wizard"

    mandate_ids = fields.Many2many(comodel_name="ext.mandate")

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        context = self.env.context or {}
        res = super().default_get(fields_list)

        if res.get("message", False):
            return res

        mode = context.get("mode", "end_date")

        model = context.get("active_model", False)
        if not model:
            return res

        ids = (
            context.get("active_ids")
            or (context.get("active_id") and [context.get("active_id")])
            or []
        )

        if mode == "reactivate":
            mandate_ids = self.env[model].browse(ids)
            if any(not m.ext_assembly_id.active for m in mandate_ids):
                res["message"] = _("Some of the assemblies are no longer active!")
        return res
