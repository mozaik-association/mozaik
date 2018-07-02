# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestEmailTemplate(TransactionCase):

    def test_default_values(self):
        """
        check for default value for several fields
        """
        # Give an instance to the user
        int_instance = self.browse_ref('mozaik_structure.int_instance_01')
        self.env.user.partner_id.int_instance_m2m_ids = int_instance
        # Cretae a template
        vals = {
            'name': 'Sébastien parmi les hommes...',
        }
        tmpl = self.env['email.template'].create(vals)
        # Check for default value
        self.assertEqual(tmpl.model_id.model, 'email.coordinate')
        self.assertIn(self.env.user, tmpl.res_users_ids)
        self.assertEqual(tmpl.int_instance_id, int_instance)
