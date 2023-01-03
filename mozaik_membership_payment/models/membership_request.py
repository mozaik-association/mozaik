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
    def _get_states_to_save(self):
        """
        Returns a list of states for which, if membership request of type 'm'
        is paid, we do not want to reach the next state IMMEDIATELY in the
        statechart (because it will be done when dealing with the payment).
        """
        return [self.env.ref("mozaik_membership.former_member")]

    def _validate_request_membership_with_checks(self, partner):
        self.ensure_one()
        paid_transactions = self.transaction_ids.filtered(lambda s: s.state == "done")
        save_state = (
            paid_transactions
            and partner.membership_state_id in self._get_states_to_save()
            and self.request_type == "m"
        )
        result_type_id = None
        if save_state:
            result_type_id = self.result_type_id
            self.result_type_id = self.membership_state_id

        res = super(MembershipRequest, self)._validate_request_membership_with_checks(
            partner
        )

        if save_state:
            self.result_type_id = result_type_id

        if self.transaction_ids:
            active_memberships = partner.membership_line_ids.filtered(
                lambda s: s.active
            )
            active_memberships.transaction_ids = self.transaction_ids
            if paid_transactions:
                paid_transactions._mark_membership_as_paid(
                    paid_transactions.acquirer_reference
                )
                for pt in paid_transactions:
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
        former_member = self.env.ref("mozaik_membership.former_member").code
        supporter = self.env.ref("mozaik_membership.supporter").code
        member_candidate = self.env.ref("mozaik_membership.member_candidate").code
        event = None
        if (
            partner.membership_state_id.code
            in [former_member, supporter, member_candidate]
            and request_type == "m"
            and self.env.context.get("tx_paid")
        ):
            event = "paid"
        return event
