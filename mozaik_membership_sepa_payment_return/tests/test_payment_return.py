# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestMembership(TransactionCase):
    def setUp(self):
        super().setUp()
        self.harry = self.env["res.partner"].create({"name": "Harry Potter"})
        self.harry_bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "BE12 1234 5678 8975",
                "partner_id": self.harry.id,
            }
        )
        self.mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.harry_bank.id,
                "signature_date": fields.Date.today(),
            }
        )
        self.mandate.validate()

    def test_recognize_partner(self):
        """
        Create a payment return for Harry and recognize the partner.
        2. Correct data but account formatted in another way -> Recognize it.
        2. Wrong account -> Do not recognize it.
        """
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
            }
        )
        pay_ret._recognize_partners()
        self.assertEqual(pay_ret.partner_id, self.harry)

    def test_recognize_partner_no_acc_number_formatting(self):
        """
        Create a payment return for Harry with a badly formatted account
        number but recognize the partner.
        """
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": "be12123456788975",
                "partner_name": "Harry Potter",
            }
        )
        pay_ret._recognize_partners()
        self.assertEqual(pay_ret.partner_id, self.harry)

    def test_not_recognize_partner_wrong_acc_number(self):
        """
        Create a payment return for Harry with a wrong account
        number: do not recognize the partner.
        """
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number.replace("1", "3"),
                "partner_name": "Harry Potter",
            }
        )
        pay_ret._recognize_partners()
        self.assertFalse(pay_ret.partner_id)

    def test_not_recognize_partner_wrong_name(self):
        """
        Create a payment return for Harry with a partial name only:
         do not recognize the partner.
        """
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry",
            }
        )
        pay_ret._recognize_partners()
        self.assertFalse(pay_ret.partner_id)

    def test_auto_process_failed_no_partner_id(self):
        """
        Try to process automatically the payment return, but no partner_id
        was set -> Failed
        """
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
            }
        )
        pay_ret._filter_and_process_refusal()
        self.assertEqual(pay_ret.state, "error")
        self.assertEqual(
            pay_ret.error_message, "Partner must be set on the payment return."
        )

    def test_auto_process_failed_no_membership_line(self):
        """
        Try to process automatically the payment return, but no membership line
        on partner_id
        -> Failed
        """
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
                "partner_id": self.harry.id,
            }
        )
        pay_ret._filter_and_process_refusal()
        self.assertEqual(pay_ret.state, "error")
        self.assertEqual(
            pay_ret.error_message,
            "No membership line to process found automatically. "
            "Please process this line manually.",
        ),

    def test_auto_process_failed_membership_line_not_member(self):
        """
        Try to process automatically the payment return, but partner is not
        a member nor a 'special' former member
        -> Failed
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.env["int.instance"]
                ._get_default_int_instance()
                .id,
                "state_id": self.ref("mozaik_membership.member_candidate"),
            }
        ).action_add()
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
                "partner_id": self.harry.id,
            }
        )
        pay_ret._filter_and_process_refusal()
        self.assertEqual(pay_ret.state, "error")
        self.assertEqual(
            pay_ret.error_message,
            "No membership line to process found automatically. "
            "Please process this line manually.",
        )

    def test_auto_process_membership_line_former_member_break(self):
        """
        Make Harry a former member (break) with a member state before (another day)
        -> Process the payment return normally.
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.env["int.instance"]
                ._get_default_int_instance()
                .id,
                "state_id": self.ref("mozaik_membership.member"),
                "date_from": fields.Date.today() - relativedelta(days=1),
            }
        ).action_add()
        self.harry.membership_line_ids.filtered("active").paid = True
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.env["int.instance"]
                ._get_default_int_instance()
                .id,
                "state_id": self.ref("mozaik_membership.break_former_member"),
            }
        ).action_add()
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
                "partner_id": self.harry.id,
            }
        )
        pay_ret._filter_and_process_refusal()
        self.assertEqual(pay_ret.state, "done")
        self.assertEqual(self.mandate.state, "cancel")
        self.assertFalse(
            self.harry.membership_line_ids.filtered(
                lambda ml: ml.state_id.code == "member"
            ).paid
        )

    def test_auto_process_membership_line_former_member_break_not_member_before(self):
        """
        Make Harry a former member (break) with no member state before
        -> Failed
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.env["int.instance"]
                ._get_default_int_instance()
                .id,
                "state_id": self.ref("mozaik_membership.break_former_member"),
            }
        ).action_add()
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
                "partner_id": self.harry.id,
            }
        )
        pay_ret._filter_and_process_refusal()
        self.assertEqual(pay_ret.state, "error")
        self.assertEqual(
            pay_ret.error_message,
            "No membership line to process found automatically. "
            "Please process this line manually.",
        )

    def test_auto_process_failed_membership_line_not_paid(self):
        """
        Try to process automatically the payment return, but active membership line
        is not paid
        -> Failed
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.env["int.instance"]
                ._get_default_int_instance()
                .id,
                "state_id": self.ref("mozaik_membership.member"),
                "price": 10,
            }
        ).action_add()
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
                "partner_id": self.harry.id,
            }
        )
        pay_ret._filter_and_process_refusal()
        self.assertEqual(pay_ret.state, "error")
        self.assertEqual(
            pay_ret.error_message,
            "Selected membership line is not paid. "
            "Please process this line manually.",
        )

    def test_auto_process_failed_amount_dont_correspond(self):
        """
        Try to process automatically the payment return, but active membership line
        is not paid
        -> Failed
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.env["int.instance"]
                ._get_default_int_instance()
                .id,
                "state_id": self.ref("mozaik_membership.member"),
                "price": 10,
            }
        ).action_add()
        self.harry.membership_line_ids.filtered("active").paid = True
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
                "partner_id": self.harry.id,
                "amount": 5,
            }
        )
        pay_ret._filter_and_process_refusal()
        self.assertEqual(pay_ret.state, "error")
        self.assertEqual(
            pay_ret.error_message,
            "Amount on membership line doesn't correspond, "
            "please process this line manually.",
        )

    def test_auto_process_succeed(self):
        """
        Succeed processing the payment return automatically
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.env["int.instance"]
                ._get_default_int_instance()
                .id,
                "state_id": self.ref("mozaik_membership.member"),
                "price": 10,
            }
        ).action_add()
        self.harry.membership_line_ids.filtered("active").paid = True
        pay_ret = self.env["payment.return"].create(
            {
                "account_number": self.harry_bank.acc_number,
                "partner_name": "Harry Potter",
                "partner_id": self.harry.id,
                "amount": 10,
            }
        )
        pay_ret._filter_and_process_refusal()
        self.assertEqual(pay_ret.state, "done")
        self.assertEqual(self.mandate.state, "cancel")
        self.assertFalse(self.harry.membership_line_ids[0].paid)
