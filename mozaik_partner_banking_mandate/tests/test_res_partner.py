# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env["account.banking.mandate"].search([]).unlink()
        self.bank_account_1 = self.env.ref("account_payment_mode.res_partner_12_iban")
        self.bank_account_2 = self.env.ref("account_payment_mode.res_partner_2_iban")
        self.partner_1 = self.bank_account_1.partner_id
        self.partner_2 = self.bank_account_2.partner_id

    def test_create_not_valid_mandate(self):
        """
        Create a not valid mandate => Partner doesn't have flag
        """
        self.env["account.banking.mandate"].create(
            {"partner_bank_id": self.bank_account_1.id}
        )
        self.assertFalse(self.partner_1.has_valid_mandate)

    def test_unlink_mandate(self):
        """
        Unlink mandates => partner looses his flag if he has no more mandate
        """
        mandate_1 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.bank_account_1.id,
                "signature_date": "2015-01-01",
                "state": "valid",
            }
        )
        mandate_2 = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.bank_account_1.id,
                "signature_date": "2015-01-01",
                "state": "valid",
            }
        )
        self.assertTrue(self.partner_1.has_valid_mandate)
        mandate_1.unlink()
        self.assertTrue(self.partner_1.has_valid_mandate)
        mandate_2.unlink()
        self.assertFalse(self.partner_1.has_valid_mandate)

    def test_edit_mandate_bank_account(self):
        """
        Edit mandate bank account => 1st partner looses his flag, 2nd partner gains flag
        """
        mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.bank_account_1.id,
                "signature_date": "2015-01-01",
                "state": "valid",
            }
        )
        self.assertTrue(self.partner_1.has_valid_mandate)
        self.assertFalse(self.partner_2.has_valid_mandate)
        mandate.write({"partner_bank_id": self.bank_account_2.id})
        self.assertFalse(self.partner_1.has_valid_mandate)
        self.assertTrue(self.partner_2.has_valid_mandate)

    def test_edit_bank_account_partner(self):
        """
        Edit bank account partner => 1st partner looses his flag, 2nd partner gains flag
        """
        self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": self.bank_account_1.id,
                "signature_date": "2015-01-01",
                "state": "valid",
            }
        )
        self.assertTrue(self.partner_1.has_valid_mandate)
        self.assertFalse(self.partner_2.has_valid_mandate)
        self.bank_account_1.write({"partner_id": self.partner_2.id})
        self.assertFalse(self.partner_1.has_valid_mandate)
        self.assertTrue(self.partner_2.has_valid_mandate)
