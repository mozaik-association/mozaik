# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from anybox.testing.openerp import SharedSetupTransactionCase


class test_duplicate_analysis_report(SharedSetupTransactionCase):

    _data_files = (
        'data/users_demo.xml',
    )

    _module_ns = 'ecolo'

    def setUp(self):
        super(test_duplicate_analysis_report, self).setUp()

        self.env['ir.model'].clear_caches()
        self.env['ir.model.data'].clear_caches()
        self.partner_obj = self.env['res.partner']
        self.user_obj = self.env['res.users']
        self.email_coordinate_obj = self.env['email.coordinate']
        self.dar_obj = self.env['duplicate.analysis.report']
        self.group_obj = self.env['res.groups']

    def test_get_partner_ids(self):
        partner_ids = self.dar_obj._get_partner_ids()
        self.assertTrue(len(partner_ids) > 0, 'Should find a partner')
        partner = self.env.ref('%s.partner_of_user_test' % self._module_ns)
        self.assertTrue(
            partner.id in partner_ids,
            'Configurator should be into the recipients')
