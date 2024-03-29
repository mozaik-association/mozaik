# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestEmailTemplate(TransactionCase):
    def test_default_values(self):
        """
        Check for default value for several fields
        """
        # Give an instance to the user
        int_instance = self.browse_ref("mozaik_structure.int_instance_01")
        self.env.user.partner_id.int_instance_m2m_ids = int_instance
        # Create a template
        vals = {
            "name": "Sébastien parmi les hommes...",
        }
        tmpl = self.env["mail.template"].with_context(active_test=False).create(vals)
        # Check for default values
        self.assertEqual(tmpl.model_id.model, "res.partner")
        tmpl.invalidate_cache()
        # Since the current user is inactive, the default owner is admin.
        self.assertFalse(self.env.user.active)
        self.assertIn(self.env.ref("base.user_admin"), tmpl.res_users_ids)
        self.assertEqual(tmpl.int_instance_id, int_instance)
