# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):

    def test_mandate_count(self):
        """
        Check the number of mandate of an assembly linked to a partner
        """
        legal_person = self.env.ref('mozaik_structure.res_partner_legal_01')
        mandate_count = legal_person.ext_mandate_count
        self.assertEquals(mandate_count, 2)

    def test_assembly_count(self):
        """
        Check the number of assembly linked to a partner
        """
        legal_person = self.env.ref('mozaik_structure.res_partner_legal_01')
        assembly_count = legal_person.ext_assembly_count
        self.assertEquals(assembly_count, 1)
