# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    event_registrations_count = fields.Integer(
        "Number of Events",
        compute="_compute_event_registrations_count",
        groups="event.group_event_user",
        help="Number of events the partner has participated.",
    )

    def _compute_event_registrations_count(self):
        self.event_registrations_count = 0
        if not self.user_has_groups("event.group_event_user"):
            return
        for partner in self:
            partner.event_registrations_count = self.env["event.event"].search_count(
                [("registration_ids.associated_partner_id", "child_of", partner.ids)]
            )

    def action_event_registrations_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("event.action_event_view")
        action["context"] = {}
        action["domain"] = [
            ("registration_ids.associated_partner_id", "child_of", self.ids)
        ]
        return action
