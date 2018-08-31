# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
from odoo.tests.common import TransactionCase
from ..models.mass_mailing import MSG_KO, MSG_OK


class TestMassMailing(TransactionCase):

    def setUp(self):
        super(TestMassMailing, self).setUp()
        self.distri_list_obj = self.env['distribution.list']
        self.ml_obj = self.env['mail.mass_mailing']
        self.distri_list_line_obj = self.env['distribution.list.line']
        self.partner_obj = self.env['res.partner']
        self.partner_model = self.env.ref("base.model_res_partner")
        self.partner_id_field = self.env.ref("base.field_res_partner_id")

    def test_try_unsubscribe_url(self):
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
        for n in range(2):
            msg = mailing._try_update_opt(partner)
            if n == 0:
                self.assertEquals(msg, MSG_OK, 'Should be unsubscribe')
            elif n == 1:
                self.assertEquals(
                    msg, MSG_KO,
                    'URL for an already unsubscribed partner will fail')
        with self.assertRaises(ValueError):
            self.ml_obj._try_update_opt(partner)
