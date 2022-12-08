# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestMembershipRequest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.bank_account_1 = self.env.ref("account_payment_mode.res_partner_12_iban")
        self.bank_account_2 = self.env.ref("account_payment_mode.res_partner_2_iban")
        self.partner_1 = self.bank_account_1.partner_id
        self.partner_2 = self.bank_account_2.partner_id

    def test_check_auto_validate_wrong_account_number(self):
        """
        MR cannot be autovalidated if account number
        is already linked to another partner
        """
        mr = self.env["membership.request"].create(
            {
                "partner_id": self.partner_1.id,
                "lastname": self.partner_1.lastname,
                "email": "test@mail.com",
                "bank_account_number": self.bank_account_2.acc_number,
            }
        )
        auto_val, failure_reason = mr._check_auto_validate(True)
        self.assertFalse(auto_val)
        expected_failure_reason = (
            "Bank account already linked to partner {name} ({id})"
        ).format(name=self.partner_2.name, id=self.partner_2.id)
        self.assertEqual(failure_reason, expected_failure_reason)

    def test_check_auto_validate_account_number(self):
        """
        Validate MR with bank_account creates mandate
        """
        mr = self.env["membership.request"].create(
            {
                "partner_id": self.partner_1.id,
                "lastname": self.partner_1.lastname,
                "email": "test@mail.com",
                "bank_account_number": self.bank_account_1.acc_number,
            }
        )
        mr._auto_validate(True)
        self.assertEqual("validate", mr.state)
        self.assertTrue(
            self.bank_account_1.mandate_ids.filtered(lambda m: m.state == "valid")
        )

    def test_mr_create_bank_account_and_mandate(self):
        """
        Upon MR validation, unrecognized bank accounts
        are created as well as new mandates
        """
        mr = self.env["membership.request"].create(
            {
                "partner_id": self.partner_1.id,
                "lastname": self.partner_1.lastname,
                "email": "test@mail.com",
                "bank_account_number": "BE78 4242 4242 4242 4242 4242 424",
            }
        )
        mr.validate_request()
        self.assertEqual("validate", mr.state)
        partner_bank = self.env["res.partner.bank"].search(
            [("acc_number", "=", "BE78 4242 4242 4242 4242 4242 424")], limit=1
        )
        self.assertEqual(partner_bank.partner_id.id, self.partner_1.id)
        mandate = self.env["account.banking.mandate"].search(
            [("partner_bank_id", "=", partner_bank.id)], limit=1
        )
        self.assertEqual(mandate.partner_id.id, self.partner_1.id)
        self.assertEqual(mandate.state, "valid")
