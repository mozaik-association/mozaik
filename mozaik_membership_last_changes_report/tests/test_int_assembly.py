# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestIntAssembly(SavepointCase):
    def test_get_summary_recipients(self):
        """
        Check for the recipients of the summary mail
        regarding the summary_mails_recipient field
        of the mandate category
        """
        # get an internal assembly and its categories
        assembly = self.browse_ref("mozaik_structure.int_assembly_02")
        cats = (
            self.env["int.mandate"]
            .search([("int_assembly_id", "=", assembly.id)])
            .mapped("mandate_category_id")
        )

        # Update mandate categories: no recipient
        cats.write({"summary_mails_recipient": False})
        # Check for recipients: False
        recipients = assembly._get_summary_recipients()
        self.assertFalse(recipients)

        # Update mandate categories: all are recipients
        cats.write({"summary_mails_recipient": True})
        # Check for recipients: True
        recipients = assembly._get_summary_recipients()
        self.assertTrue(recipients)
