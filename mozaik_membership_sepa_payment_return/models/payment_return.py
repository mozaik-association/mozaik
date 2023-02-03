# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.base.models.res_bank import sanitize_account_number


class PaymentReturn(models.Model):

    _name = "payment.return"
    _inherit = "mail.thread"
    _description = "Payment Return"

    date = fields.Date(default=fields.Date.today)
    amount = fields.Float()
    account_number = fields.Char("Bank Account Number", required=True)
    sanitized_account_number = fields.Char(
        compute="_compute_sanitized_account_number",
        store=True,
        help="Keep the account number without spaces and in upper characters.",
    )
    partner_name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("error", "Error")],
        required=True,
        default="draft",
        tracking=True,
    )
    error_message = fields.Text(tracking=True)
    active_membership_line_id = fields.Many2one("membership.line")

    def name_get(self):
        res = []
        for record in self:
            display_name = "%s - %s" % (record.account_number, record.partner_name)
            res.append((record.id, display_name))
        return res

    @api.depends("account_number")
    def _compute_sanitized_account_number(self):
        for rec in self:
            rec.sanitized_account_number = sanitize_account_number(rec.account_number)

    def _recognize_partners(self):
        """
        Find a partner having the same bank account and the same name.
        """
        for payment_return in self:
            res = self.env["res.partner.bank"].search(
                [
                    (
                        "sanitized_acc_number",
                        "=",
                        payment_return.sanitized_account_number,
                    ),
                    "|",
                    ("acc_holder_name", "=ilike", payment_return.partner_name),
                    ("partner_id.name", "=ilike", payment_return.partner_name),
                ],
            )
            if len(res) > 1:
                payment_return.message_post(
                    body=_(
                        "Trying to recognize a partner. Result: "
                        "Several bank accounts found for this account number "
                        "and partner combination."
                    )
                )
            elif len(res) == 0:
                payment_return.message_post(
                    body=_(
                        "Trying to recognize a partner. Result: "
                        "No bank account found for this account number "
                        "and partner combination."
                    )
                )
            else:
                payment_return.message_post(
                    body=_("Trying to recognize a partner. Result: Partner recognized.")
                )
                payment_return.partner_id = res.partner_id

    def _set_to_error(self, error_message):
        self.write(
            {
                "state": "error",
                "error_message": error_message,
            }
        )

    def _filter_payment_returns(self):
        """
        Check conditions to process automatically. If a condition is not checked,
        go into error state and fill the error_message field.
        :return: a recordset with payment returns that check all conditions.

        Conditions to check:
        1. payment return state is not 'done'
        2. partner_id is set on the payment.return
        3. partner_id has a single active membership line
        4. this membership line has 'member' code
        5. this active membership line is paid
        6. amount on this membership line corresponds to the amount of the
        payment return
        """
        recs = self.browse()
        for payment_return in self:
            if payment_return.state == "done":
                continue
            if not payment_return.partner_id:
                payment_return._set_to_error(
                    _("Partner must be set on the payment return.")
                )
                continue
            partner_id = payment_return.partner_id
            membership_line = partner_id.membership_line_ids.filtered("active")
            if len(membership_line) > 1:
                payment_return._set_to_error(
                    _(
                        "Several active membership lines. Please process this line manually."
                    )
                )
                continue
            if not membership_line:
                payment_return._set_to_error(
                    _("No active membership line. Please process this line manually.")
                )
                continue
            if membership_line.state_id.code != "member":
                payment_return._set_to_error(
                    _(
                        "Active membership line is not in 'Member' state. "
                        "Please process this line manually."
                    )
                )
                continue
            if not membership_line.paid:
                payment_return._set_to_error(
                    _(
                        "Active membership line is not paid. Please process this line manually."
                    )
                )
                continue
            if not abs(payment_return.amount) == membership_line.price:
                payment_return._set_to_error(
                    _(
                        "Amount on membership line doesn't correspond, "
                        "please process this line manually."
                    )
                )
                continue
            # Set the active membership line on the record and add it
            # to the recordset
            payment_return.active_membership_line_id = membership_line
            recs |= payment_return
        return recs

    def _send_notification_email(self):
        mail_template_id = self.env.ref(
            "mozaik_membership_sepa_payment_return.mail_template_partner_payment_refusal"
        )
        for payment_return in self:
            mail_template_id.send_mail(payment_return.id)

    def _process_refusal(self):
        """
        Process the SEPA direct debit refusal:

        1. Mark active membership lines as unpaid
        2. Delete banking mandates after having checked that they are linked
           to the correct partner.
        3. Email the partner
        4. Set the state 'Done'
        """
        self.mapped("active_membership_line_id").mark_as_unpaid()

        for payment_return in self:
            mandates = self.env["account.banking.mandate"].search(
                [
                    ("format", "=", "sepa"),
                    ("partner_id", "=", payment_return.partner_id.id),
                    (
                        "partner_bank_id.sanitized_acc_number",
                        "=",
                        payment_return.sanitized_account_number,
                    ),
                ]
            )
            mandates.write({"state": "cancel"})
            for mandate in mandates:
                mandate.message_post(
                    body=_("Mandate cancelled due to a payment return.")
                )

        self._send_notification_email()
        self.write({"state": "done", "error_message": False})

    def _filter_and_process_refusal(self):
        """
        Filter payment returns and call _process_refusal on the
        ones that can be processed automatically.
        """
        self._filter_payment_returns()._process_refusal()

    def confirm_manually_processed(self):
        self._send_notification_email()
        self.write({"state": "done"})
