# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    transaction_ids = fields.Many2many(
        string="Transaction", comodel_name="payment.transaction"
    )
    payment_link = fields.Char(compute="_compute_payment_link")

    @api.depends("amount", "partner_id", "reference", "request_type")
    def _compute_payment_link(self):
        wizard_obj = self.env["payment.link.wizard"]
        for m in self:
            # when used as an onchange, id is not set
            if m.id and m.amount and m.reference and m.request_type == "m":
                m.payment_link = (
                    wizard_obj.with_context(
                        active_model="membership.request", active_id=m.id
                    )
                    .new()
                    .link
                )
            else:
                m.payment_link = False

    @api.model
    def _validate_request_membership(self, mr, partner):
        res = super(MembershipRequest, self)._validate_request_membership(mr, partner)
        if mr.transaction_ids:
            active_memberships = partner.membership_line_ids.filtered(
                lambda s: s.active
            )
            active_memberships.transaction_ids = mr.transaction_ids
            if mr.transaction_ids.filtered(lambda s: s.state == "done"):
                mr.transaction_ids.filtered(
                    lambda s: s.state == "done"
                )._mark_membership_as_paid(mr.transaction_ids.acquirer_reference)
        return res
