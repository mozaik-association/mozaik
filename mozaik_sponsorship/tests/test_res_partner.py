# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.harry = cls.env["res.partner"].create({"name": "Harry Potter"})
        cls.ron = cls.env["res.partner"].create({"name": "Ron Weasley"})
        cls.hermione = cls.env["res.partner"].create({"name": "Hermione Granger"})
        cls.yesterday = date.today() - relativedelta(days=1)

    def test_harry_sponsors_ron(self):
        """
        Mark Harry as a sponsor for Ron.
        Check that Ron becomes Harry's godchild
        """
        self.ron.sponsor_id = self.harry
        self.assertEqual(self.harry.sponsor_godchild_ids.ids, [self.ron.id])
        self.assertEqual(self.ron.sponsorship_date, date.today())

    def test_sponsorship_date(self):
        """
        1. Ron is Harry sponsor -> sponsorship_date is today.
        2. Update sponsorship_date to yesterday and make Hermione become Harry's sponsor
        -> sponsorship_date didn't change
        3. Delete sponsor_id -> sponsorship_date was deleted.
        4. Fill sponsorship_date without sponsor_id -> ValidationError
        """
        # 1.
        self.harry.write({"sponsor_id": self.ron})
        self.assertEqual(self.harry.sponsorship_date, date.today())
        # 2.
        self.harry.sponsorship_date = self.yesterday
        self.harry.sponsor_id = self.hermione
        self.assertEqual(self.harry.sponsorship_date, self.yesterday)
        # 3.
        self.harry.sponsor_id = False
        self.assertFalse(self.harry.sponsorship_date)
        # 4.
        with self.assertRaises(ValidationError):
            self.harry.sponsorship_date = date.today()

    def test_sponsor_id_and_sponsorship_date(self):
        """
        Write Ron as Harry sponsor, with sponsorship date equal to yesterday.
        Ensure that sponsorship date wasn't changed to default value (today).
        """
        self.harry.write(
            {
                "sponsor_id": self.ron.id,
                "sponsorship_date": self.yesterday,
            }
        )
        self.assertEqual(self.harry.sponsorship_date, self.yesterday)
