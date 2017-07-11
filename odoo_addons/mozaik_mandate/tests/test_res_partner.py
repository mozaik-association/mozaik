# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from anybox.testing.openerp import SharedSetupTransactionCase


class test_res_partner(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'mozaik_mandate'

    def setUp(self):
        super(test_res_partner, self).setUp()
        self.res_partner = self.env['res.partner']

    def test_mandate_count(self):
        """
        Check the number of mandate of an assembly linked to a partner
        """
        legal_person = self.env.ref('%s.res_partner_rtbf' % self._module_ns)
        mandate_count = legal_person.ext_mandate_count
        self.assertEquals(mandate_count, 3)

    def test_assembly_count(self):
        """
        Check the number of assembly linked to a partner
        """
        legal_person = self.env.ref('%s.res_partner_rtbf' % self._module_ns)
        assembly_count = legal_person.ext_assembly_count
        self.assertEquals(assembly_count, 2, 'Should have 2 assembly')
