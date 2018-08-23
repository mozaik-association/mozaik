# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
from odoo.tests.common import TransactionCase
from odoo import SUPERUSER_ID


class TestMailMail(TransactionCase):

    def setUp(self):
        super(TestMailMail, self).setUp()
        self.distri_list_obj = self.env['distribution.list']
        self.mail_mail_obj = self.env['mail.mail']
        self.ml_obj = self.env['mail.mass_mailing']
        self.distri_list_line_obj = self.env['distribution.list.line']
        self.partner_obj = self.env['res.partner']
        self.user_obj = self.env['res.users']
        self.admin = self.env.ref('base.partner_root')
        self.partner_model = self.env.ref("base.model_res_partner")
        self.users_model = self.env.ref("base.model_res_users")
        self.partner_id_field = self.env.ref("base.field_res_partner_id")

    def test_get_unsubscribe_url(self):
        vals = {
            'name': str(uuid4()),
        }
        partner = self.partner_obj.create(vals)
        partner_model = self.partner_model
        vals = {
            'name': str(uuid4()),
            'dst_model_id': partner_model.id,
            'newsletter': False,
        }
        dist_list = self.distri_list_obj.create(vals)
        vals = {
            'name': str(uuid4()),
            'src_model_id': partner_model.id,
            'domain': "[('id', 'in', [%d])]" % partner.id,
            'distribution_list_id': dist_list.id,
            'bridge_field_id': self.partner_id_field.id,
        }
        self.distri_list_line_obj.create(vals)
        vals = {
            'name': 'Test',
            'contact_ab_pc': 100,
            'mailing_model_id': self.partner_model.id,
            'state': 'draft',
            'reply_to_mode': 'email',
            'reply_to': 'Test <test@example.com>',
            'distribution_list_id': dist_list.id,
            'email_from': 'Test <test@test.com>'
        }
        mailing = self.ml_obj.create(vals)
        vals = {
            'body': '<p>test</p>',
            'model': 'res.partner',
            'recipient_ids': [(4, self.admin.id)],
            'record_name': False,
            'attachment_ids': [],
            'mailing_id': mailing.id,
            'notification': True,
            'auto_delete': True,
            'body_html': '<p>test</p>',
            'no_auto_thread': False,
            'reply_to': 'Test <test@example.com>',
            'author_id': partner.id,
            'res_id': partner.id,
            'email_from': 'Test <test@example.com>',
            'subject': 'Test'
        }
        mail = self.mail_mail_obj.create(vals)
        url = mail._get_unsubscribe_url('')
        self.assertNotIn('/newsletter', url, 'Should have native url')
        vals = {
            'newsletter': True,
        }
        dist_list.write(vals)

        url = mail._get_unsubscribe_url('')
        self.assertIn('/newsletter', url, 'Should have newsletter url')
        user_model = self.users_model
        vals = {
            'partner_path': 'partner_id',
            'dst_model_id': user_model.id,
        }
        dist_list.write(vals)
        vals = {
            'model': 'res.users',
            'res_id': SUPERUSER_ID,
        }
        admin = self.user_obj.browse(SUPERUSER_ID)
        mail.write(vals)
        url = mail._get_unsubscribe_url('')
        self.assertIn(
            'res_id=%s' % admin.partner_id.id, url,
            'Should have partner_id of the user')
        vals = {
            'partner_path': 'wrong_value',
        }
        dist_list.write(vals)
        url = mail._get_unsubscribe_url('')
        self.assertFalse(url, 'Should not have url due to bad partner_path')
