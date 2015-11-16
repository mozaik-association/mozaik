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
import tempfile
import csv
import base64


class TestThesaurusTermsLoader(SharedSetupTransactionCase):

    def setUp(self):
        super(TestThesaurusTermsLoader, self).setUp()
        self.thesaurus_terms_loader_model = self.env['thesaurus.terms.loader']
        self.thesaurus_term_model = self.env['thesaurus.term']
        self.thesaurus = self.env['thesaurus']

    def _get_csv_content(self, data_file):
        tmp = tempfile.NamedTemporaryFile(
            prefix='Extract', suffix=".csv", delete=False)
        f = open(tmp.name, "r+")
        writer = csv.writer(f, delimiter=';')
        writer.writerows(data_file)
        f.close()
        f = open(tmp.name, "r")
        csv_content = f.read()
        f.close()
        return base64.encodestring(csv_content)

    def test_cu_terms(self):
        data_file = [
            ['100000000', 'Name1', ''],
            ['100000001', 'Name2', '100000000'],
            ['100000002', 'Name3', '100000001'],
            ['100000003', 'Name4', '100000001'],
        ]
        csv_content = self._get_csv_content(data_file)
        vals = {
            'file_terms': csv_content,
        }
        ttlm_id = self.thesaurus_terms_loader_model.create(vals)

        domain = [
            '|', '|', '|',
            ('ext_identifier', '=', '100000000'),
            ('ext_identifier', '=', '100000001'),
            ('ext_identifier', '=', '100000002'),
            ('ext_identifier', '=', '100000003'),
        ]
        t_ids = self.thesaurus_term_model.search(domain)
        self.assertFalse(t_ids)
        ttlm_id.load_terms()
        t_ids = self.thesaurus_term_model.search(domain)
        self.assertEqual(len(t_ids), 4, 'Should have 4 terms created')
        self.assertEqual(
            t_ids[1].parent_m2m_ids.id, t_ids[0].id,
            'Parent Relation should be represented')
        data_file = [
            ['100000000', 'Modified', 'other'],
            ['100000002', 'Name3', 'other'],
            ['100000004', 'NEW', 'other'],
        ]
        csv_content = self._get_csv_content(data_file)
        vals = {
            'file_terms': csv_content,
        }
        ttlm_id = self.thesaurus_terms_loader_model.create(vals)
        ttlm_id.load_terms()
        domain = [
            ('ext_identifier', '=', '100000004'),
        ]
        t_ids = self.thesaurus_term_model.search(domain)
        self.assertTrue(t_ids)
        domain = [
            ('ext_identifier', '=', '100000000'),
        ]
        t_ids = self.thesaurus_term_model.search(domain)
        self.assertTrue(t_ids)
        self.assertEqual(t_ids.name, 'Modified', 'Should be the modified')
