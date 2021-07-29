# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
from odoo.tests.common import TransactionCase


class TestMassMailing(TransactionCase):

    def test_unsubscribe_from_mass_mailing(self):
        vals = {
            'name': str(uuid4()),
        }
        partner = self.env['res.partner'].create(vals)
        partner_model_id = self.ref("base.model_res_partner")
        vals = {
            'name': str(uuid4()),
            'dst_model_id': partner_model_id,
            'newsletter': False,
        }
        dist_list = self.env['distribution.list'].create(vals)
        vals = {
            'name': str(uuid4()),
            'src_model_id': partner_model_id,
            'domain': "[('id', 'in', [%d])]" % partner.id,
            'distribution_list_id': dist_list.id,
            'bridge_field_id': self.ref("base.field_res_partner_id"),
        }
        self.env['distribution.list.line'].create(vals)
        vals = {
            'name': 'Test',
            'mailing_model_id': partner_model_id,
            'distribution_list_id': dist_list.id,
        }
        mailing = self.env['mail.mass_mailing'].create(vals)
        # unsubscribe partner
        mailing.update_opt_out(False, [partner.id], True)
        self.assertNotIn(partner, dist_list.res_partner_opt_in_ids)
        self.assertIn(partner, dist_list.res_partner_opt_out_ids)
        return
