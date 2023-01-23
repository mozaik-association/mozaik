# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestPartner(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_find_email_with_underscore(self):
        """
        When using 'ilike' in search method, _ is not escaped.
        But when using '=ilike' in search method, _ is escaped
        and considered as a normal character.
        """
        self.env["res.partner"].create({"name": "Omar Sy", "email": "omar.sy@test.com"})
        self.env["res.partner"].create({"name": "Omar Sy", "email": "omar_sy@test.com"})

        res = self.env["res.partner"].search([("email", "ilike", "omar.sy")])
        self.assertEqual(len(res), 1)
        res = self.env["res.partner"].search([("email", "ilike", "omar_sy")])
        self.assertEqual(len(res), 2)

        res = self.env["res.partner"].search([("email", "=ilike", "omar_sy@test.com")])
        self.assertEqual(len(res), 1)
