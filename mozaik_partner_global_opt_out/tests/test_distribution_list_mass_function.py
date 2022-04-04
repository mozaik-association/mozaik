# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
from io import StringIO

from odoo.tests.common import TransactionCase


class TestDistributionListMassFunction(TransactionCase):
    def setUp(self):
        super().setUp()
        # Not blacklisted partner
        self.omar_sy = self.env["res.partner"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omar.sy@test.com",
            }
        )
        # Blacklisted partner
        self.jean_dujardin = self.env["res.partner"].create(
            {
                "lastname": "Dujardin",
                "firstname": "Jean",
                "email": "jean.dujardin@test.com",
                "global_opt_out": True,
            }
        )
        # Distribution list containing both partners
        model_contact = self.env["ir.model"].search([("model", "=", "res.partner")])
        self.dist_list = self.env["distribution.list"].create(
            {
                "name": "Test distribution list",
                "dst_model_id": model_contact.id,
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        dst_list_line_tmpl = self.env["distribution.list.line.template"].create(
            {
                "name": "Two partners",
                "src_model_id": model_contact.id,
                "domain": "[('id', 'in', [%d, %d])]"
                % (self.omar_sy.id, self.jean_dujardin.id),
            }
        )
        self.dist_list.write(
            {
                "to_include_distribution_list_line_ids": [
                    (
                        0,
                        0,
                        {
                            "distribution_list_line_tmpl_id": dst_list_line_tmpl.id,
                            "bridge_field_id": self.env["ir.model.fields"]
                            .search(
                                [
                                    ("model_id", "=", model_contact.id),
                                    ("name", "=", "id"),
                                ]
                            )
                            .id,
                        },
                    )
                ]
            }
        )

    def test_email_csv_without_blacklisted(self):
        """
        Do the mass action to export Email coordinates to csv.
        Do not include blacklisted partners.
        Only Omar Sy should be present
        """
        wiz = self.env["distribution.list.mass.function"].create(
            {
                "trg_model": "email.coordinate",
                "e_mass_function": "csv",
                "include_opt_out_contacts": False,
                "distribution_list_id": self.dist_list.id,
            }
        )
        wiz.mass_function()
        csv_content = base64.b64decode(wiz.export_file)

        reader = csv.DictReader(StringIO(csv_content.decode("utf-8")))
        rows = []
        for row in reader:
            rows.append(row)
        self.assertEqual(len(rows), 1)

    def test_email_csv_with_blacklisted(self):
        """
        Do the mass action to export Email coordinates to csv.
        Do include blacklisted partners.
        Both partners should be present
        """
        wiz = self.env["distribution.list.mass.function"].create(
            {
                "trg_model": "email.coordinate",
                "e_mass_function": "csv",
                "include_opt_out_contacts": True,
                "distribution_list_id": self.dist_list.id,
            }
        )
        wiz.mass_function()
        csv_content = base64.b64decode(wiz.export_file)

        reader = csv.DictReader(StringIO(csv_content.decode("utf-8")))
        rows = []
        for row in reader:
            rows.append(row)
        self.assertEqual(len(rows), 2)
