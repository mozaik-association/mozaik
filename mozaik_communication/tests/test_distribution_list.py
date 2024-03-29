# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from uuid import uuid4

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase
from odoo.tools.misc import mute_logger

_logger = logging.getLogger(__name__)


class TestDistributionList(SavepointCase):
    def setUp(self):
        super().setUp()
        self.user_obj = self.env["res.users"]
        self.partner_obj = self.env["res.partner"]
        self.dl_obj = self.env["distribution.list"]
        self.mail_obj = self.env["mail.mail"]
        self.int_instance_obj = self.env["int.instance"]
        self.evr_lst_id = self.browse_ref("mozaik_communication.everybody_list")
        self.partner_model_id = self.ref("base.model_res_partner")
        self.usr = self.create_an_officier()

    def create_an_officier(self):
        # create the partner
        name = str(uuid4())
        vals = {
            "name": name,
        }
        partner = self.partner_obj.create(vals)
        default_instance_id = self.int_instance_obj._get_default_int_instance()
        # create the user
        vals = {
            "name": name,
            "login": name,
            "partner_id": partner.id,
            "company_id": self.ref("base.main_company"),
            "groups_id": [
                (
                    6,
                    0,
                    [
                        self.ref("mozaik_communication.res_groups_communication_user"),
                        self.ref("mozaik_address.res_groups_address_reader"),
                    ],
                )
            ],
            "int_instance_m2m_ids": [(6, 0, [default_instance_id.id])],
        }
        return self.user_obj.create(vals)

    def test_only_owner_forward(self):
        email = "alibaba@test.eu"

        # not all users can modify mass_mailings
        self.usr.groups_id = [(4, self.ref("base.group_system"))]

        # set email after to avoid MailDeliveryException
        self.usr.partner_id.email = email
        self.usr.partner_id.flush()

        # take a DL where user is not an owner nor an allowed partner
        dl = self.evr_lst_id
        msg = {
            "email_from": "<%s>" % email,
            "subject": "Just a test",
            "body": "body",
        }
        forward = dl._distribution_list_forwarding(msg)
        self.assertFalse(forward)

        # add user to the owner
        vals = {"res_users_ids": [(4, self.usr.id)]}
        dl.write(vals)
        forward = dl._distribution_list_forwarding(msg)
        self.assertTrue(forward)

        # remove user from owners but add it as allowed partner
        vals = {
            "res_users_ids": [(3, self.usr.id, False)],
            "res_partner_ids": [(6, 0, [self.usr.partner_id.id])],
        }
        dl.write(vals)
        forward = dl._distribution_list_forwarding(msg)
        self.assertTrue(forward)

        # take a legal person without a responsible user
        partner = self.browse_ref("mozaik_communication.res_partner_cmpy_1")
        # add it an email coordinate
        email = "emmanuel.vals.noway@rf.fr"
        partner.email = email
        # use it as a sender
        msg["email_from"] = email
        forward = dl._distribution_list_forwarding(msg)
        self.assertFalse(forward)

        # make the legal person an allowed partner of the DL
        vals = {
            "res_partner_ids": [(4, partner.id)],
        }
        dl.write(vals)
        forward = dl._distribution_list_forwarding(msg)
        self.assertFalse(forward)

        # add it a responsible user
        vals = {
            "responsible_user_id": self.usr.id,
        }
        partner.write(vals)
        forward = dl._distribution_list_forwarding(msg)
        self.assertTrue(forward)

        # inactive the user
        self.usr.active = False
        forward = dl._distribution_list_forwarding(msg)
        self.assertFalse(forward)

        # reactive the user
        self.usr.active = True
        # but with the same ec as the legal person
        self.usr.partner_id.email = email
        forward = dl._distribution_list_forwarding(msg)
        self.assertFalse(forward)
        return

    def test_newsletter_code_unique(self):
        newsletter = self.browse_ref(
            "mozaik_communication.distribution_list_newsletter"
        )
        vals = dict(
            name="Newsletter Sample 2",
            code=newsletter.code,
            newsletter=True,
        )
        with self.assertRaises(ValidationError), mute_logger("odoo.sql_db"):
            self.dl_obj.create(vals)
        return

    def test_get_complex_distribution_list_ids(self):
        # create a vip email
        thierry = self.browse_ref("mozaik_address.res_partner_thierry")
        thierry.email = "x23@example.com"
        # create a vip address
        paul = self.browse_ref("mozaik_address.res_partner_paul")
        paul.address_address_id = self.ref("mozaik_address.address_4")

        dl = self.evr_lst_id
        dl_usr = dl.with_user(user=self.usr.id)
        partner_obj = self.partner_obj

        # res.partner, admin
        a_mains, a_alternatives = dl._get_complex_distribution_list_ids()
        a_partners = self.partner_obj.search([("is_company", "=", False)])
        self.assertFalse(a_alternatives)
        self.assertEqual(a_mains, a_partners)

        dom = [
            ("is_company", "=", False),
        ]

        # res.partner, other user
        u_mains, __ = dl_usr._get_complex_distribution_list_ids()
        u_partners = partner_obj.with_user(user=self.usr.id).search(dom)
        self.assertEqual(u_mains, u_partners)

        context = dict(
            main_object_domain=[],
            main_target_model="res.partner",
            alternative_object_field="address_address_id",
            alternative_object_domain=[("email", "=", False)],
            alternative_target_model="address.address",
        )
        dl_ctx = dl.with_context(context)
        dl_usr.with_context(context)

        # email_coordinate_id, postal_coordinate_id, admin
        ac_mains, ac_alternatives = dl_ctx._get_complex_distribution_list_ids()
        self.assertIn(thierry, ac_mains)
        self.assertIn(paul.address_address_id, ac_alternatives)
        dom = [
            ("is_company", "=", False),
            ("email", "!=", False),
        ]
        ac_partners = partner_obj.search(dom)
        ac_emails = ac_partners
        self.assertEqual(ac_mains.filtered(lambda s: s.email), ac_emails)
        dom = [
            ("is_company", "=", False),
            ("email", "=", False),
            ("address", "!=", False),
        ]
        ac_partners = partner_obj.search(dom)
        ac_postals = ac_partners.mapped("address_address_id")
        self.assertEqual(ac_alternatives, ac_postals)

        return
