# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4

from odoo.tests.common import TransactionCase


class TestMassMailing(TransactionCase):
    def setUp(self):
        super(TestMassMailing, self).setUp()

        vals = {
            "name": str(uuid4()),
        }
        self.partner = self.env["res.partner"].create(vals)

        self.partner_model_id = self.ref("base.model_res_partner")
        vals = {
            "name": str(uuid4()),
            "dst_model_id": self.partner_model_id,
            "newsletter": False,
        }
        self.dist_list = self.env["distribution.list"].create(vals)

        self.dist_list_line_tmpl = self.env["distribution.list.line.template"].create(
            {
                "name": str(uuid4()),
                "src_model_id": self.partner_model_id,
                "domain": "[('id', 'in', [%d])]" % self.partner.id,
            }
        )
        vals = {
            "distribution_list_line_tmpl_id": self.dist_list_line_tmpl.id,
            "distribution_list_id": self.dist_list.id,
            "bridge_field_id": self.ref("base.field_res_partner__id"),
        }
        self.dist_list_line = self.env["distribution.list.line"].create(vals)

        vals = {
            "name": "Test",
            "subject": "Test",
            "mailing_model_id": self.partner_model_id,
            "distribution_list_id": self.dist_list.id,
        }
        self.mailing = self.env["mailing.mailing"].create(vals)

    def test_unsubscribe_from_mass_mailing(self):
        # unsubscribe partner
        self.mailing.update_opt_out(False, [self.partner.id], True)
        self.assertNotIn(self.partner, self.dist_list.res_partner_opt_in_ids)
        self.assertIn(self.partner, self.dist_list.res_partner_opt_out_ids)
        return

    def test_mass_mailing_with_distribution_list(self):
        distribution_list_model_id = self.ref(
            "mass_mailing_distribution_list.model_distribution_list"
        )
        self.mailing.write(
            {
                "mailing_model_id": distribution_list_model_id,
                "distribution_list_id": self.dist_list,
            }
        )
        self.mailing._onchange_distribution_list_id()
        self.assertEqual(self.mailing.mailing_model_real, "res.partner")
        self.assertEqual(self.dist_list_line.domain, self.mailing.mailing_domain)
