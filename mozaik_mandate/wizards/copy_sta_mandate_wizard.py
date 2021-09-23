# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from .abstract_copy_mandate_wizard import WIZARD_AVAILABLE_ACTIONS


class CopyStaMandateWizard(models.TransientModel):

    _inherit = "abstract.copy.mandate.wizard"
    _name = "copy.sta.mandate.wizard"
    _description = "Copy Sta Mandate Wizard"

    _mandate_assembly_foreign_key = "sta_assembly_id"

    mandate_id = fields.Many2one(comodel_name="sta.mandate", string="State Mandate")
    assembly_id = fields.Many2one(
        comodel_name="sta.assembly",
        string="State Assembly",
    )
    sta_assembly_category_id = fields.Many2one(
        related="new_mandate_category_id.sta_assembly_category_id",
    )
    new_assembly_id = fields.Many2one(
        comodel_name="sta.assembly", string="New State Assembly"
    )
    instance_id = fields.Many2one(string="State Instance")
    is_legislative = fields.Boolean(default=False)
    legislature_id = fields.Many2one(
        comodel_name="legislature", string="Legislature", ondelete="cascade"
    )

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)
        context = self.env.context

        ids = (
            context.get("active_id")
            and [context.get("active_id")]
            or context.get("active_ids")
            or []
        )
        model = context.get("active_model", False)
        if not model:
            return res

        for mandate in self.env[model].browse(ids):
            if (
                mandate.sta_assembly_id.is_legislative
                and res["action"] == WIZARD_AVAILABLE_ACTIONS[0][0]
            ):
                res["message"] = _("Renew not allowed on a legislative mandate")

            if res["action"] == WIZARD_AVAILABLE_ACTIONS[0][0]:
                assembly_id = mandate.sta_assembly_id
                domain = [
                    (
                        "power_level_id",
                        "=",
                        assembly_id.assembly_category_id.power_level_id.id,
                    ),
                    ("start_date", ">", fields.datetime.now()),
                ]
                legislature_id = self.env["legislature"].search(domain, limit=1).id
            else:
                legislature_id = mandate.legislature_id.id

            res["legislature_id"] = legislature_id
            res["is_legislative"] = mandate.sta_assembly_id.is_legislative
            if res["is_legislative"]:
                res.pop("new_assembly_id", False)
            break
        return res

    @api.onchange("legislature_id")
    def onchange_legislature_id(self):
        self.ensure_one()
        self.start_date = False
        self.deadline_date = False
        if self.legislature_id:
            self.start_date = self.legislature_id.start_date
            self.deadline_date = self.legislature_id.deadline_date

    def _copy_mandate(self, vals):
        """
        Renew a mandate
        """
        self.ensure_one()
        vals["legislature_id"] = self.legislature_id.id
        return super()._copy_mandate(vals)
