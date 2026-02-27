# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.mozaik_membership_request_autovalidate_light.tests.test_membership_request import (  # noqa: B950 pylint: disable=line-too-long
    TestMembershipRequest as BaseTestMembershipRequest,
)


class TestMembershipRequest(BaseTestMembershipRequest):
    def test_light_autoval_payment(self):
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omar.sy@test.com",
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
