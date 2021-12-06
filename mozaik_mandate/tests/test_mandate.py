# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestMandate(SavepointCase):
    def test_avoid_duplicate_mandate_category(self):
        """
        Test unique name of mandate category
        """
        data = dict(type="sta", name="category_01")
        self.env["mandate.category"].create(data)
        _logger = logging.getLogger("odoo.sql_db")
        previous_level = _logger.level
        _logger.setLevel(logging.CRITICAL)
        self.assertRaises(ValidationError, self.env["mandate.category"].create, data)
        _logger.setLevel(previous_level)

    def test_invalidate_mandates(self):
        """
        Test mandate closing and invalidation
        """
        m1 = self.env.ref("mozaik_mandate.stam_thierry_communal_2012")
        m2 = self.env.ref("mozaik_mandate.stam_thierry_bourgmestre_2012")
        mandates = m1 | m2
        self.assertFalse(any(mandates.mapped("end_date")))

        mandates.action_invalidate()
        self.assertFalse(any(mandates.mapped("active")))
        self.assertEqual(mandates.mapped("end_date"), mandates.mapped("deadline_date"))

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
