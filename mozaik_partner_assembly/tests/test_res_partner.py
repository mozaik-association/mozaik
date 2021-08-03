# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def test_check_is_assembly(self):
        """
        Check consistency between is_assembly and is_company
        """
        # C=True, A=True: Ok
        tastevin = self.env["res.partner"].create(
            {
                "name": "Confrérie des chevaliers du Tastevin",
                "is_company": True,
                "is_assembly": True,
            }
        )
        # C=True, A=False: Ok
        tastevin.write(
            {
                "is_assembly": False,
            }
        )
        # C=False, A=False: Ok
        tastevin.write(
            {
                "is_company": False,
            }
        )
        # C=False, A=True: Nok
        self.assertRaises(
            exceptions.ValidationError,
            tastevin.write,
            vals={
                "is_assembly": True,
            },
        )
        return
