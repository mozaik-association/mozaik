# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.mozaik_membership_request_autovalidate_light.tests.test_membership_request import (  # noqa: B950 pylint: disable=line-too-long
    TestMembershipRequest as BaseTestMembershipRequest,
)


class TestMembershipRequest(BaseTestMembershipRequest):
    def test_light_autoval(self):
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@test.com",
                "gender": "male",
                "request_type": "m",
                "amount": 22,
                "reference": "1234",
                "auto_validate_after_payment": True,
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertFalse(failure_reason)
        self.assertTrue(mr.light_mr_id)
        self.assertEqual(mr.state, "light_autoval")
        self.assertFalse(mr.active)
        self.assertEqual(mr.light_mr_id.state, "validate")
        self.assertFalse(mr.light_mr_id.active)
        self.assertEqual(mr.light_mr_id.partner_id, self.omar_sy)
        self.assertFalse(mr.auto_validate_after_payment)
        self.assertTrue(mr.light_mr_id.auto_validate_after_payment)

    def test_light_autoval_after_payment(self):
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@test.com",
                "gender": "male",
                "request_type": "m",
                "amount": 22,
                "reference": "1234",
                "auto_validate_after_payment": True,
            }
        )
        # Create payment data
        company = self.env.company
        account_bank = self.env["account.account"].create(
            {
                "name": "Test Bank",
                "code": "X1020",
                "user_type_id": self.env.ref("account.data_account_type_liquidity").id,
                "reconcile": True,
                "company_id": company.id,
            }
        )
        bank_journal = self.env["account.journal"].create(
            {
                "name": "Test Bank Journal",
                "code": "TBJ",
                "type": "bank",
                "company_id": company.id,
                "default_account_id": account_bank.id,
            }
        )
        acquirer = self.env.ref("payment.payment_acquirer_odoo_by_adyen")
        acquirer.journal_id = bank_journal
        # Create payment transaction
        self.omar_sy.country_id = self.belgium
        pt = self.env["payment.transaction"].create(
            {
                "amount": 22.0,
                "currency_id": self.env.ref("base.EUR").id,
                "partner_id": self.omar_sy.id,
                "acquirer_id": acquirer.id,
                "reference": "TEST-TX-001",
                "membership_request_ids": [(4, mr.id)],
            }
        )
        self.assertEqual(
            mr.state,
            "confirm",
            "MR shouldn't be validated as payment transaction isn't done",
        )
        # Mark payment transaction as done
        pt.state = "done"
        pt._post_process_after_done()  # Normally called by portal
        self.assertEqual(mr.state, "light_autoval")
        self.assertEqual(mr.light_mr_id.state, "validate")
