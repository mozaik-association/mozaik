# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    transaction_ids = fields.Many2many(
        string="Transaction", comodel_name="payment.transaction"
    )
    payment_link = fields.Char(compute="_compute_payment_link")

    @api.depends("price", "partner_id", "reference")
    def _compute_payment_link(self):
        wizard_obj = self.env["payment.link.wizard"]
        for m in self:
            m.payment_link = (
                wizard_obj.with_context(active_model="membership.line", active_id=m.id)
                .new()
                .link
            )
