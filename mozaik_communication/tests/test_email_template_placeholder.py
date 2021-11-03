# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestEmailTemplatePlaceholder(TransactionCase):
    def test_default_values(self):
        """
        check for default value for some fields
        """
        # Create a placeholder
        vals = {
            "name": "Et Dieu créa la femme...",
        }
        ph = self.env["email.template.placeholder"].create(vals)
        # Check for default value
        self.assertEqual(ph.model_id.model, "res.partner")
        self.assertEqual(ph.placeholder, "${object.}")
