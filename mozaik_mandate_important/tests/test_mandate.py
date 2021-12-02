# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestMandate(SavepointCase):
    def test_is_important(self):
        """
        When creating an external mandate, if no value is set for
        is_important flag. The system should set the value of related
        assembly.
        """
        mandate_category_id = self.env.ref("mozaik_mandate.mc_membre_effectif_ag")
        partner_id = self.env.ref("mozaik_address.res_partner_marc")
        ext_assembly = self.env.ref("mozaik_structure.ext_assembly_01")

        ext_assembly.is_important = True

        data = {
            "mandate_category_id": mandate_category_id.id,
            "partner_id": partner_id.id,
            "ext_assembly_id": ext_assembly.id,
            "start_date": "2016-12-20",
            "deadline_date": "2018-12-19",
        }

        mandate = self.env["ext.mandate"].create(data)
        self.assertTrue(mandate.is_important)
