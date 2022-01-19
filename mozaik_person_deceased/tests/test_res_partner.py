# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.paul = self.browse_ref("mozaik_address.res_partner_paul")
        self.marc = self.browse_ref("mozaik_address.res_partner_marc")

        # Paul and Marc become co-residents
        self.co_res = self.env["co.residency"].create(
            {
                "line": "Test co residency",
                "line2": "Two inhabitants",
                "partner_ids": [(4, self.paul.id), (4, self.marc.id)],
            }
        )
        self.paul.write({"email": "paul@test.com"})

    def test_check_death_date_not_in_future(self):
        """
        Checks that an error is raised if death date is in the future.
        """
        with self.assertRaises(ValidationError):
            wizard = (
                self.env["deceased.partner"]
                .with_context({"default_partner_id": self.paul.id})
                .create(
                    {
                        "death_date": fields.Date.today() + relativedelta(days=1),
                    }
                )
            )
            wizard.doit()

    def test_paul_died(self):
        """
        Mark Paul as deceased.
        Check that
        - partner is archived,
        - email is erased,
        - address and co-residency are erased,
        - death parameters are set up.
        """

        # Check that all parameters were set before death.
        self.assertTrue(self.paul.active)
        self.assertTrue(self.paul.email)
        self.assertTrue(self.paul.address_address_id)
        self.assertTrue(self.paul.co_residency_id)

        # Encode Paul's death
        wizard = (
            self.env["deceased.partner"]
            .with_context({"default_partner_id": self.paul.id})
            .create(
                {
                    "death_date": fields.Date.today() - relativedelta(days=1),
                }
            )
        )
        wizard.doit()

        self.assertFalse(self.paul.active)
        self.assertFalse(self.paul.email)
        self.assertFalse(self.paul.address_address_id)
        self.assertFalse(self.paul.co_residency_id)
        self.assertTrue(self.paul.is_deceased)
        self.assertEqual(
            self.paul.death_date, fields.Date.today() - relativedelta(days=1)
        )
