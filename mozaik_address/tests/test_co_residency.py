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
