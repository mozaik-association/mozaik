# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestEmailTemplatePlaceholder(TransactionCase):

    def test_default_values(self):
        """
        check for default value for some fields
        """
        # Cretae a placeholder
        vals = {
            'name': 'Et Dieu créa la femme...',
        }
        ph = self.env['email.template.placeholder'].create(vals)
        # Check for default value
        self.assertEqual(ph.model_id.model, 'email.coordinate')
        self.assertEqual(ph.placeholder, '${object.partner_id.}')
