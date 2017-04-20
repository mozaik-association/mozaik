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

from openerp import models, fields
from openerp.modules.registry import RegistryManager
from openerp.tools import SUPERUSER_ID
import openerp.tests.common as common


class TestAbstractTermFinder(common.TransactionCase):

    def _init_test_model(self, all_cls):
        pool = RegistryManager.get(common.DB)
        all_inst = []
        for cls in all_cls:
            inst = cls._build_model(pool, self.cr)
            inst._prepare_setup(self.cr, SUPERUSER_ID)
            inst._setup_base(self.cr, SUPERUSER_ID, partial=False)
            all_inst.append(inst)
        for inst in all_inst:
            inst._setup_fields(self.cr, SUPERUSER_ID)
            inst._setup_complete(self.cr, SUPERUSER_ID)
        for inst in all_inst:
            inst._auto_init(self.cr, {'module': __name__})

    def setUp(self):
        common.TransactionCase.setUp(self)

        class DummyModel(models.Model):
            _name = 'dummy.model'
            _inherit = 'abstract.term.finder'
            _description = 'Dummy Model'
            _terms = ['t_id']

            name = fields.Char(string='Name')
            t_id = fields.Many2one(
                comodel_name='thesaurus.term')

        self._init_test_model([DummyModel])
        self.dummy_model_obj = self.env['dummy.model']
        self.t_model = self.env['thesaurus.term']

    def test_abstract_finder_search(self):
        master_term_id = self.t_model.create({'name': 'test'})
        child_term_id = self.t_model.create({'name': 'test2'})
        sub_child_term_id = self.t_model.create({'name': 'test3'})
        vals = {
            'children_m2m_ids': [[6, False, [child_term_id.id]]],
        }
        master_term_id.write(vals)
        vals = {
            'parent_m2m_ids': [[6, False, [master_term_id.id]]],
            'children_m2m_ids': [[6, False, [sub_child_term_id.id]]],
        }
        child_term_id.write(vals)
        name = 'Specific Model'
        vals = {
            'name': name,
            't_id': sub_child_term_id.id,
        }
        d_id = self.dummy_model_obj.create(vals)
        domain = [('t_id', '=', master_term_id.id)]
        res_ids = self.dummy_model_obj.search(domain)
        self.assertTrue(res_ids, 'Should have a result')
        self.assertEqual(len(res_ids), 1, 'Should have 1 result')
        self.assertEqual(d_id.name, name, 'Should find with master term')
