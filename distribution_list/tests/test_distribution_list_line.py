# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
from odoo.tests.common import TransactionCase


class TestDistributionListLine(TransactionCase):

    def setUp(self):
        super(TestDistributionListLine, self).setUp()
        self.dist_list_obj = self.env['distribution.list.line']
        self.mail_template_model = self.env.ref("base.model_res_company")
        self.partner_model = self.env.ref("base.model_res_partner")
        self.dist_list = self.env['distribution.list'].create({
            'name': str(uuid4()),
            'dst_model_id': self.partner_model.id,
        })
        self.partner_id_field = self.env.ref("base.field_res_partner_id")
        self.mail_tmpl_id_field = self.env.ref(
            "base.field_res_company_partner_id")

    def test_write(self):
        """
        Check that:
        * changing only `src_model_id` will reset `domain` with `[]`
        * changing both will act like a native orm `write`
        """
        partner_model = self.partner_model
        email_template_model = self.mail_template_model
        domain = "[('is_company', '=', False)]"

        dll_values = {
            'name': str(uuid4()),
            'src_model_id': partner_model.id,
            'domain': domain,
            'distribution_list_id': self.dist_list.id,
            'bridge_field_id': self.partner_id_field.id,
        }

        dist_list_line = self.dist_list_obj.create(dll_values)
        self.assertEqual(
            dist_list_line.domain, domain, "Domains should be the same")
        # only change the src_model_id
        dist_list_line.write({
            'src_model_id': email_template_model.id,
            'bridge_field_id': self.mail_tmpl_id_field.id,
        })
        self.assertEqual(
            dist_list_line.domain, '[]', "Domain should be the default value")
        # change src_model_id and domain
        dll_values.pop('name')
        dist_list_line.write(dll_values)
        self.assertEqual(
            dist_list_line.domain, domain, "Domains should be the same")

    def test_action_show_filter_result(self):
        """
        Test that action is well returned with correct value required for
        a `get_list_from_domain`
        """
        dist_list_obj = self.dist_list_obj
        partner_model = self.partner_model

        dl_name = str(uuid4())

        dist_list_line = dist_list_obj.create({
            'name': str(uuid4()),
            'domain': "[['name', '=', '%s']]" % dl_name,
            'src_model_id': partner_model.id,
            'distribution_list_id': self.dist_list.id,
            'bridge_field_id': self.partner_id_field.id,
        })
        vals = dist_list_line.action_show_filter_result()

        self.assertEqual(vals['type'], 'ir.actions.act_window')
        self.assertEqual(vals['res_model'], 'res.partner')
