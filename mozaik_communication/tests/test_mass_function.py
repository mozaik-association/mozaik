# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from email.utils import formataddr

from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestMassFunction(SavepointCase):
    def setUp(self):
        super().setUp()
        self.evr_lst_id = self.browse_ref("mozaik_communication.everybody_list")
        self.mfct_obj = self.env["distribution.list.mass.function"]

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
        mfct_obj = self.mfct_obj
        evr_lst_id = self.evr_lst_id
        vals = {
            "trg_model": "email.coordinate",
            "e_mass_function": "email_coordinate_id",
            "distribution_list_id": evr_lst_id.id,
            "subject": "TEST1",
            "body": "<p>hello</p>",
        }
        wizard = mfct_obj.create(vals)
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
        """
        # get 2 partners
        p1 = self.browse_ref("mozaik_address.res_partner_thierry")
        p2 = self.browse_ref("mozaik_address.res_partner_pauline")
        p2.is_company = True
        # add a partner_id and a res_partner_ids to a distribution list
        dl = self.evr_lst_id
        vals = {
            "partner_id": p1.id,
            "res_partner_ids": [(6, 0, [p2.id])],
        }
        dl.write(vals)
        # from now, allowed "From" are:
        # - the parner of the list: bob
        # - authorized companies specified on the list: bobette
        # - the user because he is an owner of the list: admin

        # check for possible "From" choices
        mfct_obj = self.env["distribution.list.mass.function"].with_context(
            {
                "active_model": "distribution.list",
                "active_id": dl.id,
                "active_test": False,
            }
        )
        partners = mfct_obj._get_partner_from()
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

        # check for possible "From" choices simulating a wizard reload
        mfct_obj = mfct_obj.with_context(
            {
                "active_model": mfct_obj._name,
                "active_id": wizard.id,
                "active_test": False,
            }
        )
        partners = mfct_obj._get_partner_from()
        self.assertEqual(set(partners.ids), set(p_ids))

        vals = {
            "partner_id": False,
            "res_users_ids": [(5, 0, 0)],
        }
        dl.write(vals)
        p2.is_company = False
        # from now, allowed "From" are: nobody
        partners = mfct_obj._get_partner_from()
        # check for possible "From" choices
        self.assertFalse(partners)
        return
