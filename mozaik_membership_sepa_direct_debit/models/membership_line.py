# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    payment_order_ids = fields.Many2many(
        comodel_name="account.payment.order", string="Payment Orders"
    )

    @api.model
    def get_draft_sepa_debit_order(self):
        sepa_payment_method = self.env.ref(
            "account_banking_sepa_direct_debit.sepa_direct_debit"
        )
        sepa_payment_modes = self.env["account.payment.mode"].search(
            [("payment_method_id", "=", sepa_payment_method.id)]
        )
        debit_order = self.env["account.payment.order"].search(
            [
                ("payment_mode_id", "in", sepa_payment_modes.ids),
                ("batch_booking", "=", True),
                ("payment_type", "=", "inbound"),
                ("state", "=", "draft"),
            ],
            limit=1,
        )
        if not debit_order:
            debit_order = self.env["account.payment.order"].create(
                {
                    "payment_mode_id": sepa_payment_modes[0].id,
                    "batch_booking": True,
                    "payment_type": "inbound",
                }
            )
        return debit_order

    @api.model
    def get_unpaid_sepa_membership_lines(self):
        sql = """
            SELECT ml.id
            FROM membership_line ml
            INNER JOIN res_partner p
                ON ml.partner_id = p.id
            LEFT JOIN account_payment_order_membership_line_rel rel
                ON ml.id = rel.membership_line_id
            LEFT JOIN account_payment_order po
                ON po.id = rel.account_payment_order_id
            WHERE ml.active
            AND NOT ml.paid
            AND p.has_valid_mandate
            AND (po.id IS NULL OR po.state IN ('uploaded', 'cancel'))
        """
        self.env.cr.execute(sql)
        return self.search([("id", "in", [ml[0] for ml in self.env.cr.fetchall()])])

    @api.model
    def add_unpaid_memberships_to_debit_order(self):
        debit_order = self.get_draft_sepa_debit_order()
        unpaid_membership_lines = self.get_unpaid_sepa_membership_lines()
        for membership_line in unpaid_membership_lines:
            mandate = membership_line.partner_id.valid_mandate_id
            self.env["account.payment.line"].create(
                {
                    "order_id": debit_order.id,
                    "amount_currency": membership_line.price,
                    "partner_id": membership_line.partner_id.id,
                    "mandate_id": mandate.id,
                    "partner_bank_id": mandate.partner_bank_id.id,
                    "communication": "{state} - {date}".format(
                        state=membership_line.state_id.name,
                        date=membership_line.date_from,
                    ),
                }
            )
        unpaid_membership_lines.write({"payment_order_ids": [(4, debit_order.id)]})
