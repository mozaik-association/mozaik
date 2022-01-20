# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
import logging
from io import StringIO

from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestMassFunction(SavepointCase):
    def setUp(self):
        super().setUp()
        self.thierry = self.browse_ref("mozaik_address.res_partner_thierry")
        self.paul = self.browse_ref("mozaik_address.res_partner_paul")
        self.marc = self.browse_ref("mozaik_address.res_partner_marc")

        # Paul and Marc become co-residents.
        self.co_res = self.env["co.residency"].create(
            {
                "line": "Test co residency",
                "line2": "Two inhabitants",
                "partner_ids": [(4, self.paul.id), (4, self.marc.id)],
            }
        )

    def test_csv_export(self):
        wiz = (
            self.env["export.csv"]
            .with_context(
                active_model="res.partner", active_id=[self.thierry.id, self.paul.id]
            )
            .create({})
        )
        wiz.export()
        csv_content = base64.b64decode(wiz.export_file)

        reader = csv.DictReader(StringIO(csv_content.decode("utf-8")))
        rows = []
        for row in reader:
            rows.append(row)
        self.assertEqual(len(rows), 2)
        return

    def test_create_co_residency(self):
        """
        Check that Paul and Marc are co-residents.
        """
        self.assertEqual(self.co_res.id, self.paul.co_residency_id.id)
        self.assertEqual(self.co_res.id, self.marc.co_residency_id.id)

    def test_export_with_two_co_residents(self):
        """
        If Paul and Marc are both present in the active id list,
        and if group_by=True, only Paul data are copied in the CSV.
        """
        wiz = (
            self.env["export.csv"]
            .with_context(
                active_model="res.partner", active_id=[self.marc.id, self.paul.id]
            )
            .create({})
        )
        wiz.export(group_by=True)
        csv_content = base64.b64decode(wiz.export_file)

        reader = csv.DictReader(StringIO(csv_content.decode("utf-8")))
        rows = []
        for row in reader:
            rows.append(row)
        self.assertEqual(len(rows), 1)

    def test_export_paul(self):
        """
        If only Paul is present in the active id list,
        and if group_by=True, Paul data are copied in the CSV.
        """
        wiz = (
            self.env["export.csv"]
            .with_context(active_model="res.partner", active_id=[self.paul.id])
            .create({})
        )
        wiz.export(group_by=True)
        csv_content = base64.b64decode(wiz.export_file)

        reader = csv.DictReader(StringIO(csv_content.decode("utf-8")))
        rows = []
        for row in reader:
            rows.append(row)
        self.assertEqual(len(rows), 1)

    def test_export_marc(self):
        """
        If only Marc is present in the active id list,
        and if group_by=True, Marc data are copied in the CSV.
        """
        wiz = (
            self.env["export.csv"]
            .with_context(active_model="res.partner", active_id=[self.marc.id])
            .create({})
        )
        wiz.export(group_by=True)
        csv_content = base64.b64decode(wiz.export_file)

        reader = csv.DictReader(StringIO(csv_content.decode("utf-8")))
        rows = []
        for row in reader:
            rows.append(row)
        self.assertEqual(len(rows), 1)
