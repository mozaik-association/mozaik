# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IntAssembly(models.Model):

    _inherit = "int.assembly"

    selection_committee_ids = fields.One2many(
        comodel_name="int.selection.committee",
        inverse_name="assembly_id",
        string="Selection Committees",
        domain=[("active", "=", True)],
    )
    selection_committee_inactive_ids = fields.One2many(
        comodel_name="int.selection.committee",
        inverse_name="assembly_id",
        string="Selection Committees (Inactive)",
        domain=[("active", "=", False)],
    )

    def int_candidature_action(self):
        """
        returns the int_candidature_action, ensuring
        that the active id is the one of the int.assembly
        """
        self.ensure_one()
        # get model's action
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mozaik_committee.int_candidature_action"
        )
        action["context"] = {
            "search_default_int_assembly_id": self.id,
            "default_int_assembly_id": self.id,
        }
        return action

    def int_mandate_action(self):
        """
        returns the int_mandate_action, ensuring
        that the active id is the one of the int.assembly
        """
        self.ensure_one()
        # get model's action
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mozaik_mandate.int_mandate_action"
        )
        action["context"] = {
            "search_default_int_assembly_id": self.id,
            "default_int_assembly_id": self.id,
        }
        return action
