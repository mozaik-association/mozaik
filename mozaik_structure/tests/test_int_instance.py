# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestIntInstance(TransactionCase):
    def test_get_ancestor(self):
        federal_level = self.browse_ref("mozaik_structure.int_power_level_01")
        federal = self.browse_ref("mozaik_structure.int_instance_01")
        section_level = self.browse_ref("mozaik_structure.int_power_level_02")
        section = self.browse_ref("mozaik_structure.int_instance_02")

        section_ancestor = section._get_ancestor(federal_level)
        self.assertEqual(federal, section_ancestor)

        federal_ancestor = federal._get_ancestor(section_level)
        self.assertFalse(federal_ancestor)
