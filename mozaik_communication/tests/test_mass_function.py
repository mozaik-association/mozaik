# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import formataddr

from ..tests.common import TestCommunicationCommon

_logger = logging.getLogger(__name__)


class TestMassFunction(TestCommunicationCommon):
    def setUp(self):
        super().setUp()
        self.evr_lst_id = self.browse_ref("mozaik_communication.everybody_list")
        self.mfct_obj = self.env["distribution.list.mass.function"]
        self.address_1 = self.browse_ref("mozaik_address.address_1")

    def test_onchange_subject(self):
        evr_lst_id = self.evr_lst_id
        mfct_obj = self.mfct_obj
        vals = {
            "trg_model": "email.coordinate",
            "e_mass_function": "email_coordinate_id",
            "distribution_list_id": evr_lst_id.id,
        }
        wiz = mfct_obj.new(vals)
        self.assertFalse(wiz.mass_mailing_name)
        subject = "Le livre de la jungle"
        wiz.subject = subject
        wiz._onchange_subject()
        self.assertEqual(subject, wiz.mass_mailing_name)
        subject2 = "La guerre des étoiles"
        wiz.subject = subject2
        wiz._onchange_subject()
        self.assertEqual(subject, wiz.mass_mailing_name)
        return

    def test_save_as_template(self):
        # Create a user that can send mass mailings from mass action
        partner = self.env["res.partner"].create({"name": "Test for mass mailings"})
        vals = {
            "name": partner.name,
            "login": "superuser_mm",
            "partner_id": partner.id,
            "groups_id": [
                (
                    6,
                    0,
                    [
                        self.ref(
                            "mozaik_communication.res_groups_communication_manager_mass_mailing"
                        ),
                    ],
                )
            ],
        }
        superuser_mm = self.env["res.users"].create(vals)

        mfct_obj = self.mfct_obj
        evr_lst_id = self.evr_lst_id
        vals = {
            "trg_model": "email.coordinate",
            "e_mass_function": "email_coordinate_id",
            "distribution_list_id": evr_lst_id.id,
            "subject": "TEST1",
            "body": "<p>hello</p>",
        }
        wizard = mfct_obj.with_user(user=superuser_mm.id).create(vals)
        wizard.save_as_template()
        self.assertTrue(wizard.mail_template_id)
        self.assertEqual(wizard.mail_template_id.subject, vals["subject"])
        self.assertEqual(wizard.mail_template_id.body_html, vals["body"])
        return

    def test_email_from(self):
        """
        Check for:
        * partner_from_id content and default value
        * email_from computed value

        NOTE: change default user for this test: since OdooBot is
        archived, it doesn't appear in distribution list owners.
        """
        self.env.uid = self.env.ref("base.user_admin").id
        # get 2 partners
        p1 = self.browse_ref("mozaik_address.res_partner_thierry")
        p2 = self.browse_ref("mozaik_address.res_partner_pauline")
        p2.is_company = True
        # add a partner_id and a res_partner_ids to a distribution list
        # set the current user as an owner
        dl = self.evr_lst_id
        vals = {
            "partner_id": p1.id,
            "res_partner_ids": [(6, 0, [p2.id])],
            "res_users_ids": [(6, 0, [self.env.user.id])],
        }
        dl.write(vals)
        # from now, allowed "From" are:
        # - the parner of the list: bob
        # - authorized companies specified on the list: bobette
        # - the user because he is an owner of the list: admin

        # check for possible "From" choices
        mfct_obj = self.env["distribution.list.mass.function"].with_context(
            {
                "default_distribution_list_id": dl.id,
            }
        )
        partners = dl._get_partner_from()
        p_ids = [p1.id, p2.id, self.env.user.partner_id.id]
        self.assertEqual(set(partners.ids), set(p_ids))
        # check for default value
        def_from = mfct_obj._get_default_partner_from_id()
        self.assertEqual(def_from, self.env.user.partner_id)
        # check for email_from
        vals = {
            "partner_from_id": p2.id,
            "partner_name": "Le roi Arthur",
        }
        wizard = mfct_obj.create(vals)
        email = formataddr((vals["partner_name"], p2.email))
        self.assertEqual(email, wizard.email_from)
        return

    def test_email_bounced(self):
        """
        Set thierry email as bounced with bounced_counter = 2.
        Ask for email csv without bounced partners -> no thierry.
        Ask for email csv with a maximum number of bounced = 1 -> no thierry
        Ask for email csv with a maximum number of bounced = 2 -> thierry is present.
        """
        self.thierry.write({"email": "thierry@test.com", "email_bounced": 2})
        # Assert that Thierry is the only partner with a bounced email address
        self.assertEqual(
            len(self.env["res.partner"].search([("email_bounced", ">", 0)])), 1
        )

        wiz = self.mfct_obj.create(
            {
                "trg_model": "email.coordinate",
                "e_mass_function": "csv",
                "include_email_bounced": False,
                "distribution_list_id": self.evr_lst_id.id,
            }
        )

        wiz.mass_function()
        number_without_bounced = len(self._from_csv_get_rows(wiz))

        wiz.write({"include_email_bounced": True, "email_bounce_counter": 1})
        wiz.mass_function()
        number_with_one_bounced = len(self._from_csv_get_rows(wiz))

        wiz.email_bounce_counter = 2
        wiz.mass_function()
        number_with_two_bounced = len(self._from_csv_get_rows(wiz))

        self.assertEqual(number_without_bounced, number_with_one_bounced)
        self.assertEqual(number_without_bounced + 1, number_with_two_bounced)
