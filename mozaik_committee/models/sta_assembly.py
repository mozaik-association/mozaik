# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StaAssembly(models.Model):

    _inherit = "sta.assembly"

    selection_committee_ids = fields.One2many(
        comodel_name="sta.selection.committee",
        inverse_name="assembly_id",
        string="Selection Committees",
        domain=[("active", "=", True)],
    )
    selection_committee_inactive_ids = fields.One2many(
        comodel_name="sta.selection.committee",
        inverse_name="assembly_id",
        string="Selection Committees (Inactive)",
        domain=[("active", "=", False)],
    )

    def sta_candidature_action(self):
        """
        returns the sta_candidature_action, ensuring
        that the active id is the one of the sta.assembly
        """
        self.ensure_one()
        # get model's action
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mozaik_committee.sta_candidature_action"
        )
        action["context"] = {
            "search_default_sta_assembly_id": self.id,
            "default_sta_assembly_id": self.id,
        }
        return action

    def sta_mandate_action(self):
        """
        returns the sta_mandate_action, ensuring
        that the active id is the one of the sta.assembly
        """
        self.ensure_one()
        # get model's action
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mozaik_mandate.sta_mandate_action"
        )
        action["context"] = {
            "search_default_sta_assembly_id": self.id,
            "default_sta_assembly_id": self.id,
        }
        return action
