# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import csv
import logging
from io import StringIO

from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestCommunicationCommon(SavepointCase):
    def setUp(self):
        super().setUpClass()
        self.thierry = self.browse_ref("mozaik_address.res_partner_thierry")

    def _from_csv_get_rows(self, wizard):
        """
        Take a distribution.list.mass.function wizard
        or an export.csv wizard.
        Parse the csv_file, if existing.
        Return rows.
        """
        rows = []
        if wizard.export_file:
            csv_content = base64.b64decode(wizard.export_file)

            reader = csv.DictReader(StringIO(csv_content.decode("utf-8")))
            for row in reader:
                rows.append(row)
        return rows
