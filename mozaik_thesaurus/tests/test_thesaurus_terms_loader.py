# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from anybox.testing.openerp import SharedSetupTransactionCase


class TestThesaurusTermsLoader(SharedSetupTransactionCase):

    def setUp(self):
        super(TestThesaurusTermsLoader, self).setUp()
        self.thesaurus_terms_loader_model = self.env['thesaurus.terms.loader']
        self.thesaurus_term_model = self.env['thesaurus.term']
        self.thesaurus = self.env['thesaurus']

    def test_cu_terms(self):
        data_file = [
            ['100000000', 'Name1', 'other'],
            ['100000001', 'Name2', 'other'],
            ['100000002', 'Name3', 'other'],
            ['100000003', 'Name4', 'other'],
        ]
        domain = [
            '|', '|', '|',
            ('ext_identifier', '=', '100000000'),
            ('ext_identifier', '=', '100000001'),
            ('ext_identifier', '=', '100000002'),
            ('ext_identifier', '=', '100000003'),
        ]
        t_ids = self.thesaurus_term_model.search(domain)
        self.assertFalse(t_ids)
        self.thesaurus_terms_loader_model.cu_terms(data_file)
        t_ids = self.thesaurus_term_model.search(domain)
        self.assertEqual(len(t_ids), 4, 'Should have 4 terms created')
