# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    survey_count = fields.Integer(
        "# Surveys",
        compute="_compute_survey_count",
        groups="mozaik_survey_is_private.group_survey_child_instances",
        help="Number of surveys the partner answered.",
    )

    def _compute_survey_count(self):
        self.survey_count = 0
        if not self.user_has_groups(
            "mozaik_survey_is_private.group_survey_child_instances"
        ):
            return
        for partner in self:
            partner.survey_count = self.env["survey.survey"].search_count(
                [("user_input_ids.partner_id", "child_of", partner.ids)]
            )

    def action_survey_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("survey.action_survey_form")
        action["context"] = {}
        action["domain"] = [("user_input_ids.partner_id", "child_of", self.ids)]
        return action
