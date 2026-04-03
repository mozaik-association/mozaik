# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    mailing_trace_count = fields.Integer(
        string="Mass Mailings",
        compute="_compute_mailing_trace_count",
    )

    def _compute_mailing_trace_count(self):
        MailingTrace = self.env["mailing.trace"]
        for partner in self:
            partner.mailing_trace_count = MailingTrace.search_count(
                [("partner_id", "=", partner.id)]
            )

    def action_view_mailing_traces(self):
        self.ensure_one()
        return {
            "name": "Mailings",
            "type": "ir.actions.act_window",
            "res_model": "mailing.trace",
            "view_mode": "tree,form",
            "views": [
                (
                    self.env.ref(
                        "mozaik_mass_mailing_partner.mailing_trace_partner_tree_view"
                    ).id,
                    "tree",
                ),
                (False, "form"),
            ],
            "domain": [("partner_id", "=", self.id)],
            "context": {
                "default_partner_id": self.id,
                "search_default_partner_id": self.id,
            },
        }
