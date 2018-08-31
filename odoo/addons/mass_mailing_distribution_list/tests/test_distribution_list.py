# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
from odoo.tests.common import TransactionCase
from odoo import exceptions
from odoo.tools.safe_eval import safe_eval


class TestDistributionList(TransactionCase):

    def setUp(self):
        super(TestDistributionList, self).setUp()
        self.distri_list_obj = self.env['distribution.list']
        self.distri_list_line_obj = self.env['distribution.list.line']
        self.alias_obj = self.env['mail.alias']
        self.partner_obj = self.env['res.partner']
        self.ir_cfg_obj = self.env['ir.config_parameter']
        self.mail_obj = self.env['mail.mail']
        self.partner_model = self.env.ref("base.model_res_partner")
        self.dist_list_model = self.env.ref(
            "mass_mailing_distribution_list.model_distribution_list")
        self.partner_id_field = self.env.ref("base.field_res_partner_id")
        catchall_param = self.ir_cfg_obj.get_param('mail.catchall.domain')
        if not catchall_param:
            # create the domain alias to avoid exception during the creation
            # of the distribution list alias
            self.ir_cfg_obj.set_param('mail.catchall.domain', 'test.eu')

    def test_update_opt(self):
        """
        Check
        * update opt with out/in/wrong value
        * length of opt_(out/in)_ids after update
        :return:
        """
        vals = {
            'name': str(uuid4()),
        }
        partner = self.partner_obj.create(vals)
        vals = {
            'name': str(uuid4()),
        }
        partner2 = self.partner_obj.create(vals)
        vals = {
            'name': str(uuid4()),
            'dst_model_id': self.partner_model.id,
            'newsletter': True,
        }
        dist_list = self.distri_list_obj.create(vals)
        vals = {
            'name': str(uuid4()),
            'src_model_id': self.partner_model.id,
            'domain': "[('id', 'in', %s)]" % partner.ids,
            'distribution_list_id': dist_list.id,
            'bridge_field_id': self.partner_id_field.id,
        }
        self.distri_list_line_obj.create(vals)

        # opt in
        dist_list._update_opt(partner2, mode='in')
        self.assertEquals(
            len(dist_list.res_partner_opt_in_ids), 1,
            'Should have one opt_in_ids')

        # remove 2 ids with opt_out
        partners = partner | partner2
        dist_list._update_opt(partners, mode='out')
        self.assertEquals(
            len(dist_list.res_partner_opt_out_ids), 2,
            'Should have two opt_out_ids')
        with self.assertRaises(exceptions.ValidationError) as e:
            dist_list._update_opt(partner, mode='bad')
        self.assertIn(" is not a valid mode", e.exception.name)
        return

    def test_get_ids_from_distribution_list(self):
        """
        manage opt in/out.
        Check that
        * opt_in ids are into the res_ids
        * opt_out ids are not into the res_ids
        :return:
        """
        vals = {
            'name': str(uuid4()),
        }
        partner = self.partner_obj.create(vals)
        partner_model = self.partner_model
        vals = {
            'name': str(uuid4()),
            'dst_model_id': partner_model.id,
            'newsletter': True,
        }
        dist_list = self.distri_list_obj.create(vals)
        vals = {
            'name': str(uuid4()),
            'src_model_id': partner_model.id,
            'domain': "[('id', '=', %d)]" % partner.id,
            'distribution_list_id': dist_list.id,
            'bridge_field_id': self.partner_id_field.id,
        }
        dist_list_line = self.distri_list_line_obj.create(vals)
        targets = dist_list._get_target_from_distribution_list()
        self.assertEquals(
            len(targets), 1, 'Should have one partner into res_ids')
        # remove this partner with excluded filter
        dist_list_line.copy({
            'name': str(uuid4()),
            'distribution_list_id': dist_list.id,
            'exclude': True,
        })
        targets = dist_list._get_target_from_distribution_list()
        self.assertFalse(bool(targets), 'Should have an empty result')
        # now add it into res_partner_opt_in_ids
        dist_list._update_opt(partner, mode='in')
        targets = dist_list._get_target_from_distribution_list()
        self.assertEquals(
            len(targets), 1,
            'Should have one partner into res_ids cause of opt_in_ids')
        # now add it into opt_out_ids
        dist_list._update_opt(partner, mode='out')
        targets = dist_list._get_target_from_distribution_list()
        self.assertFalse(bool(targets), 'Should have an empty result')
        return

    def test_alias_name(self):
        """

        :return:
        """
        catchall = 'demo'
        dl_name = str(uuid4())
        # disable temporary the catchall alias
        self.ir_cfg_obj.set_param("mail.catchall.alias", '')
        # now this must raise
        with self.assertRaises(exceptions.MissingError) as e:
            self.distri_list_obj._build_alias_name(dl_name)
        self.assertEquals(
            "Please contact your Administrator to configure a "
            "'catchall' mail alias", e.exception.name)

        # re-enable the catchall alias
        self.ir_cfg_obj.set_param("mail.catchall.alias", catchall)

        # now this must produce an alias without exception
        alias_name = self.distri_list_obj._build_alias_name(dl_name)
        self.assertEqual(alias_name, '%s+%s' % (catchall, dl_name),
                         'Generated alias name should be "catchall+dl_name"')
        vals = {
            'name': dl_name,
            'dst_model_id': self.partner_model.id,
            'alias_name': alias_name,
        }
        dist_line = self.distri_list_obj.create(vals)

        self.assertFalse(
            dist_line.alias_name,
            'Without mail forwarding, alias name should be null')

        vals = {
            'mail_forwarding': True,
            'alias_name': alias_name,
        }
        dist_line.write(vals)

        self.assertEqual(
            dist_line.alias_name, alias_name,
            'Without mail forwarding, alias name should be "catchall+dl_name"')
        # Eval the alias_defaults like Odoo do it
        alias_default = dict(safe_eval(dist_line.alias_defaults))
        self.assertTrue(
            bool(alias_default.get('distribution_list_id', False)),
            'Default value should be a dictionary with the key '
            '"distribution_list_id"')
        alias_dl_id = alias_default.get('distribution_list_id')
        self.assertEquals(
            alias_dl_id, dist_line.id,
            'Distribution list ID and alias distribution list ID '
            'should be the same')
        dist_list_model = self.dist_list_model
        self.assertEqual(
            dist_line.alias_model_id.id, dist_list_model.id,
            'Alias model should be "distribution list"')
        return

    def test_message_new(self):
        msg_dict = {}
        dist_list = self.distri_list_obj.message_new(
            msg_dict, custom_values=None)
        self.assertFalse(
            bool(dist_list), 'Should not succeed without "custom_values"')
        dist_list = self.distri_list_obj.message_new(
            msg_dict, custom_values={})
        self.assertFalse(
            bool(dist_list),
            'Should not succeed without a "distribution_list_id" '
            'into "custom_values"')
        dl_name = str(uuid4())
        vals = {
            'name': dl_name,
            'dst_model_id': self.partner_model.id,
        }
        dist_list = self.distri_list_obj.create(vals)
        custom_values = {
            'distribution_list_id': dist_list.id,
        }
        result = self.distri_list_obj.message_new(
            msg_dict, custom_values=custom_values)
        self.assertEqual(
            dist_list.id, result.id,
            'Concerned distribution list should be the same '
            'as the passed present one into "custom_values"')
        vals = {
            'mail_forwarding': True,
            'alias_name': self.distri_list_obj._build_alias_name(dl_name),
        }
        dist_list.write(vals)
        msg_dict.update({
            'email_from': "<test@test.be>",
            'subject': 'test my subject',
            'body': "body",
            'attachments': [('filename', 'content')],
        })
        self.distri_list_obj.message_new(
            msg_dict, custom_values=custom_values)
        vals = {
            'name': str(uuid4()),
            'email': 'test@test.be',
        }
        partner = self.partner_obj.create(vals)
        context = self.env.context.copy()
        # Update context to keep mail.mail (then check if mail has been
        # created or not). Otherwise Odoo will delete mail.mail and we can't
        # check
        context.update({
            'default_auto_delete': False,
            'default_keep_archives': True,
        })
        self.distri_list_obj.with_context(context).message_new(
            msg_dict, custom_values=custom_values)
        mail = self.mail_obj.search([
            ('res_id', '=', partner.id),
            ('model', '=', 'res.partner'),
        ], limit=1)
        self.assertTrue(bool(mail),
                        'A mail should have been created to this partner')
        self.assertTrue(bool(mail.attachment_ids),
                        'Mail Should have an attachment')
        return

    def test_get_mailing_object(self):
        name = str(uuid4())
        email_from = '%s@test.eu' % str(uuid4())
        vals = {
            'name': name,
            'dst_model_id': self.partner_model.id,
        }
        dist_list = self.distri_list_obj.create(vals)
        vals = {
            'name': name,
            'email': email_from,
        }
        partner = self.partner_obj.create(vals)

        partner_result = dist_list._get_mailing_object('<%s>' % email_from)
        self.assertEqual(
            partner.ids, partner_result.ids, 'Partner should be the same')

        partner_result = dist_list._get_mailing_object(
            '<%s>' % email_from, mailing_model=self.partner_model.model)
        self.assertEqual(
            partner.ids, partner_result.ids, 'Partner should be the same')
        return

    def test_get_opt_res_ids(self):
        partner = self.env.ref('base.partner_root')
        results = self.distri_list_obj._get_opt_res_ids(
            'res.partner', [('id', '=', partner.id)])
        self.assertEquals(partner.ids, results.ids, 'Should be equals')
