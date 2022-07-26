# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtAssembly(models.Model):

    _inherit = "ext.assembly"

    selection_committee_ids = fields.One2many(
        comodel_name="ext.selection.committee",
        inverse_name="assembly_id",
        string="Selection Committees",
        domain=[("active", "=", True)],
    )
    selection_committee_inactive_ids = fields.One2many(
        comodel_name="ext.selection.committee",
        inverse_name="assembly_id",
        string="Selection Committees (Inactive)",
        domain=[("active", "=", False)],
    )

    def ext_candidature_action(self):
        """
        returns the ext_candidature_action, ensuring
        that the active id is the one of the ext.assembly
        """
        self.ensure_one()
        # get model's action
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mozaik_committee.ext_candidature_action"
        )
        action["context"] = {
            "search_default_ext_assembly_id": self.id,
            "default_ext_assembly_id": self.id,
        }
        return action

    def ext_mandate_action(self):
        """
        returns the ext_mandate_action, ensuring
        that the active id is the one of the ext.assembly
        """
        self.ensure_one()
        # get model's action
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mozaik_mandate.ext_mandate_action"
        )
        action["context"] = {
            "search_default_ext_assembly_id": self.id,
            "default_ext_assembly_id": self.id,
        }
        return action
