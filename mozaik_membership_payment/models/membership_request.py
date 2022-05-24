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
    auto_validate_after_payment = fields.Boolean(
        string="Auto-validation after payment",
        help="When transaction state is done, try to auto-validate the membership request",
    )

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
        paid_transactions = mr.transaction_ids.filtered(lambda s: s.state == "done")
        former_member = self.env.ref("mozaik_membership.former_member")
        save_state = (
            paid_transactions
            and partner.membership_state_id == former_member
            and mr.request_type == "m"
        )
        result_type_id = None
        if save_state:
            # when we pay a former membership, we don't the membership request
            # to advance automatically the state, it will be done by the payment
            result_type_id = mr.result_type_id
            mr.result_type_id = mr.membership_state_id

        res = super(MembershipRequest, self)._validate_request_membership(mr, partner)

        if save_state:
            mr.result_type_id = result_type_id

        if mr.transaction_ids:
            active_memberships = partner.membership_line_ids.filtered(
                lambda s: s.active
            )
            active_memberships.transaction_ids = mr.transaction_ids
            if paid_transactions:
                paid_transactions._mark_membership_as_paid(
                    paid_transactions.acquirer_reference
                )
                for pt in paid_transactions:
                    if not pt.payment_id.move_id.partner_id:
                        pt.payment_id.move_id.line_ids.write({"partner_id": partner.id})
        return res

    def _onchange_partner_id_vals_multi(
        self, is_company, request_type, partner_id, technical_name
    ):
        self.ensure_one()
        self_ctx = self
        if self.transaction_ids.filtered(lambda s: s.state == "done"):
            self_ctx = self.with_context(tx_paid=True)

        return super(MembershipRequest, self_ctx)._onchange_partner_id_vals_multi(
            is_company, request_type, partner_id, technical_name
        )

    def _get_event_get_partner_preview(self, partner, request_type):
        former_member = self.env.ref("mozaik_membership.former_member")
        event = None
        if (
            partner.membership_state_id == former_member
            and request_type == "m"
            and self.env.context.get("tx_paid")
        ):
            event = "paid"
        return event
