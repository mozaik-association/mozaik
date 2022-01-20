# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from uuid import uuid4

from odoo import exceptions
from odoo.tests.common import SavepointCase
from odoo.tools.safe_eval import safe_eval


class TestDistributionList(SavepointCase):
    def setUp(self):
        super(TestDistributionList, self).setUp()
        self.distri_list_obj = self.env["distribution.list"]
        self.distri_list_line_obj = self.env["distribution.list.line"]
        self.distri_list_line_tmpl_obj = self.env["distribution.list.line.template"]
        self.alias_obj = self.env["mail.alias"]
        self.partner_obj = self.env["res.partner"]
        self.ir_cfg_obj = self.env["ir.config_parameter"].sudo()
        self.mail_obj = self.env["mail.mail"]
        self.partner_model = self.env.ref("base.model_res_partner")
        self.dist_list_model = self.env.ref(
            "mass_mailing_distribution_list.model_distribution_list"
        )
        self.partner_id_field = self.env.ref("base.field_res_partner__id")
        catchall_param = self.ir_cfg_obj.get_param("mail.catchall.domain")
        if not catchall_param:
            # create the domain alias to avoid exception during the creation
            # of the distribution list alias
            self.ir_cfg_obj.set_param("mail.catchall.domain", "test.eu")
        vals = {
            "name": str(uuid4()),
        }
        self.partner = self.partner_obj.create(vals)
        partner_model = self.partner_model
        vals = {
            "name": str(uuid4()),
            "dst_model_id": partner_model.id,
            "newsletter": True,
        }
        self.dist_list = self.distri_list_obj.create(vals)
        self.dist_list_line_tmpl = self.distri_list_line_tmpl_obj.create(
            {
                "name": str(uuid4()),
                "src_model_id": partner_model.id,
                "domain": "[('id', '=', %d)]" % self.partner.id,
            }
        )
        vals = {
            "distribution_list_line_tmpl_id": self.dist_list_line_tmpl.id,
            "distribution_list_id": self.dist_list.id,
            "bridge_field_id": self.partner_id_field.id,
        }
        self.dist_list_line = self.distri_list_line_obj.create(vals)

    def test_update_opt(self):
        """
        Check
        * update opt with out/in/wrong value
        * length of opt_(out/in)_ids after update
        """
        partner = self.partner
        dist_list = self.dist_list
        # opt in
        dist_list._update_opt(partner.ids, mode="in")
        self.assertIn(partner, dist_list.res_partner_opt_in_ids)
        self.assertNotIn(partner, dist_list.res_partner_opt_out_ids)
        # opt_out
        dist_list._update_opt(partner.ids, mode="out")
        self.assertIn(partner, dist_list.res_partner_opt_out_ids)
        self.assertNotIn(partner, dist_list.res_partner_opt_in_ids)
        # wrong mode
        with self.assertRaises(exceptions.ValidationError) as e:
            dist_list._update_opt(partner.ids, mode="bad")
        self.assertIn(" is not a valid mode", e.exception.args[0])
        return

    def test_get_ids_from_distribution_list(self):
        """
        Check that opt_in ids are included in res_ids and
        opt_out ids are excluded from res_ids
        """
        partner = self.partner
        dist_list = self.dist_list
        targets = dist_list._get_target_from_distribution_list()
        self.assertEqual(len(targets), 1)
        # remove this partner with excluded filter
        self.dist_list_line.copy(
            default={
                "name": str(uuid4()),
                "distribution_list_id": dist_list.id,
                "exclude": True,
            }
        )
        targets = dist_list._get_target_from_distribution_list()
        self.assertFalse(targets)
        # opt in
        dist_list._update_opt(partner.ids, mode="in")
        targets = dist_list._get_target_from_distribution_list()
        self.assertEqual(len(targets), 1)
        # opt out
        dist_list._update_opt(partner.ids, mode="out")
        targets = dist_list._get_target_from_distribution_list()
        self.assertFalse(targets)
        return

    def test_alias_name(self):
        """
        Check for alias name
        """
        catchall = "demo"
        dl_name = str(uuid4())
        # try to disable temporary the catchall alias
        catchall = self.ir_cfg_obj.set_param("mail.catchall.alias", "") or catchall
        if not self.ir_cfg_obj.get_param("mail.catchall.alias"):
            # now this must raise
            with self.assertRaises(exceptions.MissingError) as e:
                self.distri_list_obj._build_alias_name(dl_name)
            self.assertEqual(
                "Please contact your Administrator to configure a "
                "'catchall' mail alias",
                e.exception.args[0],
            )
            # re-enable the catchall alias
            self.ir_cfg_obj.set_param("mail.catchall.alias", catchall)
        # now this must produce an alias without exception
        alias_name = self.distri_list_obj._build_alias_name(dl_name)
        self.assertEqual(alias_name, "%s+%s" % (catchall, dl_name))
        # create a new list
        vals = {
            "name": dl_name,
            "dst_model_id": self.partner_model.id,
            "alias_name": alias_name,
        }
        dist_list = self.distri_list_obj.create(vals)
        # without mail forwarding alias is empty
        self.assertFalse(dist_list.alias_name)
        # make it a mail forwarding list
        vals = {
            "mail_forwarding": True,
            "alias_name": alias_name,
        }
        dist_list.write(vals)
        # alias is effective
        self.assertEqual(dist_list.alias_name, alias_name)
        # Eval the alias_defaults like Odoo do it
        alias_default = dict(safe_eval(dist_list.alias_defaults))
        # the dictionary conatins a key with the list id
        self.assertEqual(alias_default["distribution_list_id"], dist_list.id)
        # alias model = distribution list
        self.assertEqual(dist_list.alias_model_id, self.dist_list_model)
        return

    def test_message_new(self):
        msg_dict = {}
        _logger = logging.getLogger(
            "odoo.addons.mass_mailing_distribution_list.models.distribution_list"
        )
        previous_level = _logger.level
        _logger.setLevel(logging.CRITICAL)
        dist_list = self.distri_list_obj.message_new(msg_dict, custom_values=None)
        _logger.setLevel(previous_level)
        # without custom value: NOK
        self.assertFalse(dist_list)

        _logger = logging.getLogger(
            "odoo.addons.mass_mailing_distribution_list.models.distribution_list"
        )
        previous_level = _logger.level
        _logger.setLevel(logging.CRITICAL)
        dist_list = self.distri_list_obj.message_new(msg_dict, custom_values={})
        _logger.setLevel(previous_level)
        # without distribution list: NOK
        self.assertFalse(dist_list)
        dl_name = str(uuid4())
        vals = {
            "name": dl_name,
            "dst_model_id": self.partner_model.id,
        }
        dist_list = self.distri_list_obj.create(vals)
        custom_values = {
            "distribution_list_id": dist_list.id,
        }
        _logger = logging.getLogger(
            "odoo.addons.mass_mailing_distribution_list.models.distribution_list"
        )
        previous_level = _logger.level
        _logger.setLevel(logging.CRITICAL)
        result = self.distri_list_obj.message_new(msg_dict, custom_values=custom_values)
        _logger.setLevel(previous_level)
        # with a distribution list: OK, result is the list
        self.assertEqual(dist_list.id, result.id)
        vals = {
            "mail_forwarding": True,
            "alias_name": self.distri_list_obj._build_alias_name(dl_name),
        }
        dist_list.write(vals)
        msg_dict.update(
            {
                "email_from": "<test@test.be>",
                "subject": "test my subject",
                "body": "body",
                "attachments": [("filename", "content")],
            }
        )
        _logger = logging.getLogger(
            "odoo.addons.mass_mailing_distribution_list.models.distribution_list"
        )
        previous_level = _logger.level
        _logger.setLevel(logging.CRITICAL)
        self.distri_list_obj.message_new(msg_dict, custom_values=custom_values)
        _logger.setLevel(previous_level)
        vals = {
            "name": str(uuid4()),
            "email": "test@test.be",
        }
        partner = self.partner_obj.create(vals)
        context = self.env.context.copy()
        # Update context to keep mail.mail (then check if mail has been
        # created or not). Otherwise Odoo will delete mail.mail and we can't
        # check
        context.update(
            {
                "default_auto_delete": False,
                "default_keep_archives": True,
            }
        )
        self.distri_list_obj.with_context(context).message_new(
            msg_dict, custom_values=custom_values
        )
        mail = self.mail_obj.search(
            [
                ("res_id", "=", partner.id),
                ("model", "=", "res.partner"),
            ],
            limit=1,
        )
        self.assertTrue(bool(mail), "A mail should have been created to this partner")
        self.assertTrue(bool(mail.attachment_ids), "Mail Should have an attachment")
        return

    def test_get_mailing_object(self):
        name = str(uuid4())
        email_from = "%s@test.eu" % str(uuid4())
        vals = {
            "name": name,
            "dst_model_id": self.partner_model.id,
        }
        dist_list = self.distri_list_obj.create(vals)
        vals = {
            "name": name,
            "email": email_from,
        }
        partner = self.partner_obj.create(vals)

        partner_result = dist_list._get_mailing_object("<%s>" % email_from)
        self.assertEqual(partner.ids, partner_result.ids, "Partner should be the same")

        partner_result = dist_list._get_mailing_object(
            "<%s>" % email_from, mailing_model=self.partner_model.model
        )
        self.assertEqual(partner.ids, partner_result.ids, "Partner should be the same")
        return

    def test_get_opt_res_ids(self):
        partner = self.env.ref("base.partner_admin")
        results = self.dist_list._get_opt_res_ids([("id", "=", partner.id)])
        self.assertEqual(partner, results)

    def test_alias_domain(self):
        vals = {
            "mail_forwarding": True,
            "alias_name": "test",
        }
        if not self.ir_cfg_obj.get_param("mail.catchall.domain"):
            with self.assertRaises(exceptions.MissingError):
                self.dist_list.write(vals)
        self.ir_cfg_obj.set_param("mail.catchall.domain", "demo")
        self.dist_list.write(vals)
        self.assertEqual(self.dist_list.alias_domain, "demo")
