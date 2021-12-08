# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    petition_count = fields.Integer(
        "# Petitions",
        compute="_compute_petition_count",
        groups="mozaik_petition.group_petition_user",
        help="Number of petitions the partner has signed.",
    )

    def _compute_petition_count(self):
        self.petition_count = 0
        if not self.user_has_groups("mozaik_petition.group_petition_user"):
            return
        for partner in self:
            partner.petition_count = self.env["petition.petition"].search_count(
                [("registration_ids.partner_id", "child_of", partner.ids)]
            )

    def action_petition_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mozaik_petition.petition_model_action"
        )
        action["context"] = {}
        action["domain"] = [("registration_ids.partner_id", "child_of", self.ids)]
        return action
