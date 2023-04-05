# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.harry = cls.env["res.partner"].create({"name": "Harry Potter"})
        cls.ron = cls.env["res.partner"].create({"name": "Ron Weasley"})

    def test_harry_sponsors_ron(self):
        """
        Mark Harry as a sponsor for Ron.
        Check that Ron becomes Harry's godchild
        """
        self.ron.sponsor_id = self.harry
        self.assertEqual(self.harry.sponsor_godchild_ids.ids, [self.ron.id])
