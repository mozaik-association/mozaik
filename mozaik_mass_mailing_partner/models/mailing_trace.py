# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailingTrace(models.Model):
    _inherit = "mailing.trace"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        compute="_compute_partner_id",
        store=True,
        index=True,
    )
    is_received = fields.Boolean(
        string="Received",
        compute="_compute_mailing_status",
        store=True,
        help="True if the mailing was sent without exception.",
    )
    is_opened = fields.Boolean(
        string="Opened",
        compute="_compute_mailing_status",
        store=True,
        help="True if the recipient opened the mailing.",
    )
    is_clicked = fields.Boolean(
        string="Clicked",
        compute="_compute_mailing_status",
        store=True,
        help="True if the recipient clicked a link in the mailing.",
    )

    @api.depends("model", "res_id")
    def _compute_partner_id(self):
        partner_model = self.env["res.partner"]
        for trace in self:
            partner = partner_model.browse()
            if trace.model == "res.partner" and trace.res_id:
                partner = partner_model.browse(trace.res_id).exists()
            trace.partner_id = partner

    @api.depends("sent", "exception", "opened", "clicked")
    def _compute_mailing_status(self):
        for trace in self:
            trace.is_received = bool(trace.sent and not trace.exception)
            trace.is_opened = bool(trace.opened)
            trace.is_clicked = bool(trace.clicked)
