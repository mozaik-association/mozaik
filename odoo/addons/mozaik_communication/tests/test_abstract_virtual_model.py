# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAbstractVirtualModel(TransactionCase):

    def test_compute_result_id(self):
        vt_model = self.env['virtual.target']
        # get a partner with some coordinates
        thierry_id = self.ref('mozaik_coordinate.res_partner_thierry')
        vt = vt_model.search(
            [('partner_id', '=', thierry_id)], limit=1)
        # build a memory record with its common_id
        vt_new = self.env['virtual.target'].new({
            'common_id': vt.common_id,
        })
        vt_new._compute_result_id()
        self.assertEqual(vt, vt_new.result_id)
        # build a memory record with a non existing common_id
        vt_new = self.env['virtual.target'].new({
            'common_id': 'Les hommes savent pourquoi !',
        })
        vt_new._compute_result_id()
        self.assertFalse(vt_new.result_id)
        return
