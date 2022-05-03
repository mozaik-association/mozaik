# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import first


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    transaction_ids = fields.Many2many(
        string="Transactions",
        comodel_name="payment.transaction",
        copy=False,
    )
    latest_transaction = fields.Many2one(
        string="Latest Transaction",
        comodel_name="payment.transaction",
        compute="_compute_latest_transaction",
        store=True,
        copy=False,
    )
    transaction_state = fields.Selection(
        string="Transaction State",
        related="latest_transaction.state",
        store=True,
        copy=False,
    )
    transaction_acquirer_id = fields.Many2one(
        string="Transaction Acquirer",
        related="latest_transaction.acquirer_id",
        store=True,
        copy=False,
    )
    payment_link = fields.Char(compute="_compute_payment_link")

    @api.depends("transaction_ids", "transaction_ids.date")
    def _compute_latest_transaction(self):
        for mr in self:
            transactions = mr.transaction_ids.filtered(lambda s: s.date).sorted(
                "date", reverse=True
            )
            mr.latest_transaction = first(transactions)

    @api.depends("amount", "partner_id", "reference", "request_type", "state")
    def _compute_payment_link(self):
        wizard_obj = self.env["payment.link.wizard"]
        for m in self:
            # when used as an onchange, id is not set
            if (
                m.id
                and m.amount
                and m.reference
                and m.request_type == "m"
                and m.state in ["draft", "confirm"]
            ):
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
