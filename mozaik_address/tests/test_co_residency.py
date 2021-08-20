# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCoResidency(TransactionCase):
    def test_co_residency_constraint(self):
        partner_j = self.env.ref("mozaik_address.res_partner_jacques")
        partner_m = self.env.ref("mozaik_address.res_partner_marc")
        partner_p = self.env.ref("mozaik_address.res_partner_pauline")
        partner_t = self.env.ref("mozaik_address.res_partner_thierry")
        partner_p2 = self.env.ref("mozaik_address.res_partner_paul")

        co_res = self.env["co.residency"].create(
            {
                "partner_ids": [
                    (4, partner_j.id),
                    (4, partner_m.id),
                ]
            }
        )

        with self.assertRaises(ValidationError):
            co_res.partner_ids += partner_p
        co_res.partner_ids -= partner_p

        with self.assertRaises(ValidationError):
            co_res.partner_ids += partner_t
        co_res.partner_ids -= partner_t

        wizard = (
            self.env["create.co.residency.address"]
            .with_context(active_ids=[partner_p2.id, partner_j.id])
            .create({})
        )

        wizard.create_co_residency()

        self.assertEqual(len(co_res.partner_ids), 3)

        co_res.line = "test"
        self.assertEqual(co_res.line, co_res.display_name)

        co_res.unlink()
        wizard = (
            self.env["create.co.residency.address"]
            .with_context(active_ids=[partner_p2.id, partner_j.id])
            .create({})
        )
        wizard.create_co_residency()

        self.assertEqual(len(partner_p2.co_residency_id.partner_ids), 2)
