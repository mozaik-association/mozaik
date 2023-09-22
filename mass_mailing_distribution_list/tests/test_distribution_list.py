# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4

from odoo import exceptions
from odoo.tests.common import SavepointCase


class TestDistributionList(SavepointCase):
    def setUp(self):
        super(TestDistributionList, self).setUp()
        self.distri_list_obj = self.env["distribution.list"]
        self.distri_list_line_obj = self.env["distribution.list.line"]
        self.distri_list_line_tmpl_obj = self.env["distribution.list.line.template"]
        self.partner_obj = self.env["res.partner"]
        self.mail_obj = self.env["mail.mail"]
        self.partner_model = self.env.ref("base.model_res_partner")
        self.dist_list_model = self.env.ref(
            "mass_mailing_distribution_list.model_distribution_list"
        )
        self.partner_id_field = self.env.ref("base.field_res_partner__id")
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

    def test_get_opt_res_ids(self):
        partner = self.env.ref("base.partner_admin")
        results = self.dist_list._get_opt_res_ids([("id", "=", partner.id)])
        self.assertEqual(partner, results)
