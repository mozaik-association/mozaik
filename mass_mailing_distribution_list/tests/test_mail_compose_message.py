# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4

from odoo.tests.common import SavepointCase


class TestMailComposeMessage(SavepointCase):
    def setUp(self):
        super(TestMailComposeMessage, self).setUp()
        self.dist_list_line_obj = self.env["distribution.list.line"]
        self.dist_list_line_tmpl_obj = self.env["distribution.list.line.template"]
        self.mass_mailing_obj = self.env["mailing.mailing"]
        self.mail_compose_message_obj = self.env["mail.compose.message"]
        self.dst_model_id = self.env.ref("base.model_res_partner")
        self.partner_id_field = self.env.ref("base.field_res_partner__id")
        vals = {
            "name": str(uuid4()),
            "dst_model_id": self.dst_model_id.id,
        }
        self.dist_list = self.env["distribution.list"].create(vals)

    def test_create_mail_compose_message(self):
        """
        If a `mail.compose.message` is create with a `mail.mass_mailing`
        that has a `distribution_list_id` then the `mail.compose.message`
        should have this `distribution_list_id` too
        :return:
        """
        dist_list = self.dist_list
        vals = {
            "name": "test",
            "subject": "test",
            "reply_to_mode": "email",
            "distribution_list_id": dist_list.id,
        }
        mass_mailing = self.mass_mailing_obj.create(vals)
        vals = {
            "subject": "test",
            "model": "res.partner",
            "email_from": "test@test.tst",
            "record_name": False,
            "composition_mode": "mass_mail",
            "mass_mailing_id": mass_mailing.id,
            "no_auto_thread": True,
        }
        mail_compose_message = self.mail_compose_message_obj.create(vals)
        self.assertEqual(
            mail_compose_message.distribution_list_id.id,
            dist_list.id,
            "Wizard should have the same distribution list than its " "mass_mailing",
        )
        return

    def test_get_mail_values(self):
        """
        If a 'mail.compose.message' has a 'distribution_list_id' and a
        'mail.mass_mailing' then this 'mail.mass_mailing' should have the same
        'distribution_list_id'
        :return:
        """
        vals = {
            "name": str(uuid4()),
            "email": "test@test.be",
        }
        partner = self.env["res.partner"].create(vals)
        dist_list = self.dist_list
        dist_list_line_tmpl = self.dist_list_line_tmpl_obj.create(
            {
                "name": str(uuid4()),
                "src_model_id": self.dst_model_id.id,
                "domain": "[('id', 'in', [%s])]" % partner.id,
            }
        )
        vals = {
            "distribution_list_line_tmpl_id": dist_list_line_tmpl.id,
            "distribution_list_id": dist_list.id,
            "bridge_field_id": self.partner_id_field.id,
        }
        self.dist_list_line_obj.create(vals)
        # mail compose message
        mass_mailing_name = str(uuid4())
        vals = {
            "model": self.dst_model_id.model,
            "email_from": "test@test.tst",
            "record_name": False,
            "composition_mode": "mass_mail",
            "distribution_list_id": dist_list.id,
            "mass_mailing_name": mass_mailing_name,
            "subject": "New Gadgets",
            "no_auto_thread": True,
        }
        mail_compose_msg = self.mail_compose_message_obj.create(vals)
        mail_compose_msg.send_mail()

        mass_mailing = self.mass_mailing_obj.search(
            [("name", "=", mass_mailing_name)], limit=1
        )
        self.assertTrue(
            bool(mass_mailing),
            "Should have a mass_mailing with the name %s" % mass_mailing_name,
        )
        self.assertEqual(
            mass_mailing.distribution_list_id.id,
            dist_list.id,
            "Should have a mass_mailing with the name %s" % mass_mailing_name,
        )
