# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from psycopg2 import IntegrityError

from odoo import exceptions
from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, mute_logger


class TestPartnerInvolvement(SavepointCase):
    def setUp(self):
        super().setUp()
        self.paul = self.env["res.partner"].create({"name": "Paul Bocuse"})
        self.ic_1 = self.browse_ref(
            "mozaik_involvement.partner_involvement_category_demo_1"
        )
        self.inv_group = self.browse_ref(
            "mozaik_involvement.res_groups_involvement_user"
        )

    def test_add_interests_on_involvement_creation(self):
        """
        Check for interests propagation when creating an involvement
        """
        # get a partner
        paul = self.paul
        # get an involvement category
        cat = self.browse_ref("mozaik_involvement.partner_involvement_category_demo_1")
        # create a term
        term_id = self.env["thesaurus.term"].create(
            {
                "name": "Bonne Bouffe !",
            }
        )
        # add it on category
        cat.write(
            {
                "interest_ids": [(4, term_id.id)],
            }
        )
        self.env["partner.involvement"].create(
            {
                "partner_id": paul.id,
                "involvement_category_id": cat.id,
            }
        )
        self.assertIn(cat.interest_ids, paul.interest_ids)

    def test_multi(self):
        """
        Check for multiple involvements
        """
        # get a partner
        paul = self.paul
        # get an involvement category
        cat = self.browse_ref("mozaik_involvement.partner_involvement_category_demo_1")
        # create an involvement
        involvement = self.env["partner.involvement"].create(
            {
                "partner_id": paul.id,
                "involvement_category_id": cat.id,
            }
        )
        # check for effective_time
        self.assertFalse(involvement.effective_time)
        # copy it: NOK
        with self.assertRaises(exceptions.UserError):
            involvement.copy()
        # allow miltiple involvements
        cat.allow_multi = True
        # check for effective_time
        self.assertTrue(involvement.effective_time)
        involvement.unlink()
        # create a new involvement
        now = (datetime.now() + timedelta(hours=-1)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT
        )
        involvement = self.env["partner.involvement"].create(
            {
                "partner_id": paul.id,
                "involvement_category_id": cat.id,
                "effective_time": now,
            }
        )
        # copy it: OK
        involvement.copy()
        # create an already existing involvement: NOK
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            test_creation = self.env["partner.involvement"].create(
                {
                    "partner_id": paul.id,
                    "involvement_category_id": cat.id,
                    "effective_time": now,
                }
            )
            test_creation.flush()

    def test_onchange_type(self):
        """
        Check for allow_multiple when changing involvement type
        """
        # create an involvement category
        cat = self.env["partner.involvement.category"].new(
            {
                "name": "Semeur, vaillants du rêve...",
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        # Set allow_multi = True
        cat.allow_multi = True
        # Change type to another type
        cat.involvement_type = "voluntary"
        cat._onchange_involvement_type()
        self.assertFalse(cat.allow_multi)

    def test_security(self):
        """
        Testing security for Partner Involvement / User group.
        A user that is owner can update and delete an involvement.
        A user that is just a follower can update but not delete the involvement.
        """
        user_test = self.env["res.users"].create(
            {
                "name": "Test user",
                "login": "TU",
            }
        )
        self.inv_group.users = [(4, user_test.id)]
        omar_sy = self.env["res.partner"].create(
            {
                "lastname": "sy",
                "firstname": "omar",
            }
        )
        involvement = self.env["partner.involvement"].create(
            {
                "partner_id": omar_sy.id,
                "involvement_category_id": self.ic_1.id,
            }
        )
        involvement_id = involvement.id

        # External user cannot write or unlink
        with self.assertRaises(AccessError):
            involvement.with_user(user_test.id).write({"note": "Test"})
        with self.assertRaises(AccessError):
            involvement.with_user(user_test.id).unlink()

        # Make the user a follower of the involvement category -> it can write but not unlink
        mail_foll = self.env["mail.followers"].create(
            {
                "res_model": "partner.involvement.category",
                "res_id": self.ic_1.id,
                "partner_id": user_test.partner_id.id,
            }
        )
        involvement.with_user(user_test.id).write({"note": "Test"})
        self.assertEqual(involvement.note, "Test")
        with self.assertRaises(AccessError):
            involvement.with_user(user_test.id).unlink()

        # Remove the user from the followers of the involvement category
        # but make it a follower of the involvement itself.
        mail_foll.unlink()
        mail_foll = self.env["mail.followers"].create(
            {
                "res_model": "partner.involvement",
                "res_id": involvement.id,
                "partner_id": user_test.partner_id.id,
            }
        )
        involvement.with_user(user_test.id).write({"note": "Testbis"})
        self.assertIn(involvement.note, "Testbis")
        with self.assertRaises(AccessError):
            involvement.with_user(user_test.id).unlink()

        # Remove the user from the followers and make it an owner
        mail_foll.unlink()
        self.ic_1.res_users_ids = [(4, user_test.id)]
        involvement.with_user(user_test.id).write({"note": "Test2"})
        self.assertIn(involvement.note, "Test2")
        involvement.with_user(user_test.id).unlink()
        self.assertFalse(
            self.env["partner.involvement"].search([("id", "=", involvement_id)])
        )
