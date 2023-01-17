# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        # A partner with an email (but without global_opt_out)
        self.omar_sy = self.env["res.partner"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omar.sy@test.com",
            }
        )

    def test_create_partner_with_opt_out(self):
        """
        Create a partner with email and directly tick opt-out
        -> created mail.blacklist

        Write on an existing partner to tick opt-out
        -> created mail.blacklist
        """
        self.env["res.partner"].create(
            {
                "lastname": "Dupont",
                "firstname": "Jean",
                "email": "j.d@test.com",
                "global_opt_out": True,
            }
        )

        self.assertEqual(
            len(self.env["mail.blacklist"].search([("email", "=", "j.d@test.com")])),
            1,
            "Mail blacklist was not created.",
        )

        self.omar_sy.write({"global_opt_out": True})
        self.assertEqual(
            len(
                self.env["mail.blacklist"].search([("email", "=", "omar.sy@test.com")])
            ),
            1,
            "Mail blacklist was not created.",
        )

    def test_undo_blacklist(self):
        """
        Tick global opt-out for omar_sy, then untick.
        Check that associated mail.blacklist is archived.
        Tick it again and check that is again archived.
        """
        self.omar_sy.write({"global_opt_out": True})
        mb = self.env["mail.blacklist"].search([("email", "=", "omar.sy@test.com")])
        self.assertTrue(mb, "Mail blacklist not found.")
        self.assertTrue(mb.active, "Mail blacklist should be active")

        self.omar_sy.write({"global_opt_out": False})
        self.assertFalse(mb.active, "Mail blacklist shouldn't be active")

        self.omar_sy.write({"global_opt_out": True})
        self.assertTrue(mb.active, "Mail blacklist should be active")

    def test_two_partners_with_same_email(self):
        """
        Create two partners with same email.
        Tick global_opt_out on one of them.
        Check that global_opt_out is also ticked on the
        second partner.
        """
        jean_dupont = self.env["res.partner"].create(
            {
                "lastname": "Dupont",
                "firstname": "Jean",
                "email": "omar.sy@test.com",
            }
        )
        self.omar_sy.write({"global_opt_out": True})
        self.assertTrue(jean_dupont.global_opt_out)

    def test_create_and_delete_mail_blacklist(self):
        """
        Partner omar_sy has an authorized email.
        We create a mail.blacklist for this email.
        We check that omar_sy.global_opt_out was set to true.

        We archive and unarchive the record. We check that global_opt_out
        always has the right value.

        We delete this mail.blacklist. Check that global_opt_out is
        False again
        """
        self.assertFalse(self.omar_sy.global_opt_out)
        mb = self.env["mail.blacklist"].create({"email": "omar.sy@test.com"})
        self.assertTrue(self.omar_sy.global_opt_out)

        mb.write({"active": False})
        self.assertFalse(self.omar_sy.global_opt_out)

        mb.write({"active": True})
        self.assertTrue(self.omar_sy.global_opt_out)

        mb.unlink()
        self.assertFalse(self.omar_sy.global_opt_out)

    def test_click_on_mail_action_blacklist_remove(self):
        """
        On a partner with global opt-out, click on
        mail_action_blacklist_remove
        """
        self.omar_sy.write({"global_opt_out": True})
        mb = self.env["mail.blacklist"].search([("email", "=", "omar.sy@test.com")])
        self.assertTrue(mb.active)

        wiz = self.env["mail.blacklist.remove"].create(
            {
                "email": self.omar_sy.email,
            }
        )
        wiz.action_unblacklist_apply()
        self.assertFalse(mb.active)
        self.assertFalse(self.omar_sy.global_opt_out)

    def test_remove_email_unticks_global_opt_out(self):
        """
        If email is removed from partner, gloabl opt-out is unticked
        and email is removed from blacklist
        """
        self.omar_sy.write({"global_opt_out": True})
        mb = self.env["mail.blacklist"].search([("email", "=", "omar.sy@test.com")])
        self.assertTrue(mb.active)

        self.omar_sy.write({"email": False})
        self.assertFalse(self.omar_sy.global_opt_out)
        self.assertFalse(mb.active)
