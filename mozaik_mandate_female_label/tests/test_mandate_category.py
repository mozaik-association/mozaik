# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestMandateCategory(SavepointCase):
    def setUp(self):
        super(TestMandateCategory, self).setUp()
        self.cat = self.browse_ref("mozaik_mandate.mc_bourgmestre")
        self.cat.female_name = "Bourgmeisje"

    def test_hook(self):
        cat = self.browse_ref("mozaik_mandate.mc_secretaire_regional")
        self.assertEqual(cat.female_name, cat.name)

    def test_name_get(self):
        cat = self.cat
        self.assertNotEqual(cat.female_name, cat.name)
        name = cat.name_get()[0][1]
        self.assertEqual(cat.name, name)
        cat = cat.with_context(gender="male")
        name = cat.name_get()[0][1]
        self.assertEqual(cat.name, name)
        cat = cat.with_context(gender="other")
        name = cat.name_get()[0][1]
        self.assertEqual(cat.name, name)
        cat = cat.with_context(gender="female")
        name = cat.name_get()[0][1]
        self.assertEqual(cat.female_name, name)

    def test_name_search(self):
        femcat = self.cat
        cat = self.env["mandate.category"]
        name = cat.name_search(name="meis")[0][1]
        self.assertEqual(femcat.name, name)
        cat = cat.with_context(gender="male")
        name = cat.name_search(name="meis")
        self.assertFalse(name)
        cat = cat.with_context(gender="other")
        name = cat.name_search(name="meis")
        self.assertFalse(name)
        cat = cat.with_context(gender="female")
        name = cat.name_search(name="meis")[0][1]
        self.assertEqual(femcat.female_name, name)
