# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
            }
        )

    def _create_mr_from_partner(self, disabled_change):
        """
        Create a membership request as if clicking on 'modification request'
        button on partner.
        Change disabled status on membership request.
        Validate membership request.
        """
        self.partner.button_modification_request()
        mr = self.env["membership.request"].search(
            [("lastname", "=", "Sy"), ("state", "=", "draft")]
        )
        self.assertEqual(len(mr), 1)
        if disabled_change:
            mr.write({"disabled_change": disabled_change})
        mr.validate_request()

    def test_disabled_change(self):
        # Force true : disabled becomes True
        self.assertFalse(self.partner.disabled)
        self._create_mr_from_partner("force_true")
        self.assertTrue(self.partner.disabled)

        # no_change : no change for disabled status
        self._create_mr_from_partner(False)
        self.assertTrue(self.partner.disabled)

        # Force true when already true : no change
        self._create_mr_from_partner("force_true")
        self.assertTrue(self.partner.disabled)

        # Force false: disabled becomes False
        self._create_mr_from_partner("force_false")
        self.assertFalse(self.partner.disabled)

        # Force false when already false : no change
        self._create_mr_from_partner("force_false")
        self.assertFalse(self.partner.disabled)
