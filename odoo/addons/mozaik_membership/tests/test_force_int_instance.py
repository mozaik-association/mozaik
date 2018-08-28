# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
from odoo.tests.common import TransactionCase


class TestForceIntInstance(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_obj = self.env['res.partner']
        self.int_instance_obj = self.env['int.instance']

    def test_force_int_instance_action(self):
        """
        Check that int_instance is well updated after process a
        `force_int_instance_action`
        """
        wiz_obj = self.env['force.int.instance']

        vals = {
            'lastname': '%s' % uuid4(),
        }

        partner = self.partner_obj.create(vals)
        int_instance = self.env.ref('mozaik_structure.int_instance_01')

        vals = {
            'partner_id': partner.id,
            'int_instance_id': int_instance.id,
        }
        wiz_id = wiz_obj.create(vals)
        wiz_id.force_int_instance_action()

        self.assertEqual(int_instance, partner.int_instance_id,
                         'Instance should be updated with forced value')
