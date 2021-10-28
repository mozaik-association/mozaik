# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
import logging
from io import StringIO

from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestMassFunction(SavepointCase):
    def test_csv_export(self):
        thierry = self.browse_ref("mozaik_address.res_partner_thierry")
        paul = self.browse_ref("mozaik_address.res_partner_paul")

        wiz = (
            self.env["export.csv"]
            .with_context(active_model="res.partner", active_id=[thierry.id, paul.id])
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
