# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMembershipRequest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.omar_sy = self.env["res.partner"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omar.sy@test.com",
            }
        )

    def test_check_constrains_force_opt_in_out(self):
        """
        If both force global opt-in and force global opt-out
        are checked, an error is raised.
        """
        with self.assertRaises(ValidationError):
            self.env["membership.request"].create(
                {
                    "partner_id": self.omar_sy.id,
                    "lastname": self.omar_sy.lastname,
                    "force_global_opt_in": True,
                    "force_global_opt_out": True,
                }
            )

    def test_force_global_opt_in(self):
        """
        Force global opt-in on membership request, if partner has
        global opt-out.
        Check that global opt-out has been removed.
        Force global opt-in again on membership request. Nothing
        happens.
        """
        self.omar_sy.write({"global_opt_out": True})
        self.assertTrue(self.omar_sy.global_opt_out)
        mr = self.env["membership.request"].create(
            {
                "partner_id": self.omar_sy.id,
                "lastname": self.omar_sy.lastname,
                "force_global_opt_in": True,
            }
        )
        mr.validate_request()
        self.assertFalse(self.omar_sy.global_opt_out)

        mr = self.env["membership.request"].create(
            {
                "partner_id": self.omar_sy.id,
                "lastname": self.omar_sy.lastname,
                "force_global_opt_in": True,
            }
        )
        mr.validate_request()
        self.assertFalse(self.omar_sy.global_opt_out)

    def test_force_global_opt_out(self):
        """
        Force global opt-out on membership request.
        Check that global opt-out has been set.
        Force global opt-out again on membership request. Nothing
        happens.
        """
        self.assertFalse(self.omar_sy.global_opt_out)
        mr = self.env["membership.request"].create(
            {
                "partner_id": self.omar_sy.id,
                "lastname": self.omar_sy.lastname,
                "force_global_opt_out": True,
            }
        )
        mr.validate_request()
        self.assertTrue(self.omar_sy.global_opt_out)

        mr = self.env["membership.request"].create(
            {
                "partner_id": self.omar_sy.id,
                "lastname": self.omar_sy.lastname,
                "force_global_opt_out": True,
            }
        )
        mr.validate_request()
        self.assertTrue(self.omar_sy.global_opt_out)
