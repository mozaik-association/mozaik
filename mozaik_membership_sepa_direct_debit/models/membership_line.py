# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    payment_line_ids = fields.One2many(
        comodel_name="account.payment.line",
        inverse_name="membership_line_id",
        string="Payment Lines",
    )

    def write(self, vals):
        res = super().write(vals)
        if not vals.get("active", True):
            self.mapped("payment_line_ids").filtered(
                lambda pl: pl.state == "draft"
            ).unlink()
        return res

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
            LEFT JOIN account_payment_line apl
                ON apl.membership_line_id = ml.id
            LEFT JOIN account_payment_order apo
                ON apl.order_id = apo.id
            WHERE ml.active
            AND NOT ml.paid
            AND p.has_valid_mandate
            AND (apl.id IS NULL OR apo.state IN ('uploaded', 'cancel'))
        """
        self.env.cr.execute(sql)
        return self.search([("id", "in", [ml[0] for ml in self.env.cr.fetchall()])])

    @api.model
    def add_unpaid_memberships_to_debit_order(self):
        debit_order = self.get_draft_sepa_debit_order()
        for membership_line in self.get_unpaid_sepa_membership_lines():
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
                    "membership_line_id": membership_line.id,
                }
            )
