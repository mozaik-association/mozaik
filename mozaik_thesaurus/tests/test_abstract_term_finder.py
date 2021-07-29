# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, fields
from odoo.tests import SavepointCase


class DummyModel(models.Model):
    _name = 'dummy.model'
    _inherit = 'abstract.term.finder'
    _description = 'Dummy Model'
    _terms = ['t_id']
    _abstract = True

    name = fields.Char()
    t_id = fields.Many2one(
        comodel_name='thesaurus.term')


class TestAbstractTermFinder(SavepointCase):
    """
    Get Odoo models to update/instantiate
    :return: list
    """
    def _get_odoo_models(self):
        """
        Get Odoo models to update/instantiate
        Order is important
        :return: list
        """
        return [DummyModel]

    def _init_test_model(self):
        """
        Function to init/create a new Odoo Model during unit test.
        :return: bool
        """
        models_cls = self._get_odoo_models()
        registry = self.env.registry
        cr = self.env.cr
        # Get the logger of the registry to disable logs who say that the
        # table doesn't exists
        _logger = logging.getLogger("odoo.modules.registry")
        previous_level = _logger.level
        _logger.setLevel(logging.CRITICAL)
        for model_cls in models_cls:
            model_cls._build_model(registry, cr)
        registry.setup_models(cr)
        names = [m._name for m in models_cls]
        registry.init_models(cr, names, self.env.context)
        _logger.setLevel(previous_level)
        return True

    def setUp(self):
        super(TestAbstractTermFinder, self).setUp()

        registry = self.registry
        # We must be in test mode before create/init new models
        registry.enter_test_mode()
        # Add the cleanup to disable test mode after this setup as finished
        self.addCleanup(registry.leave_test_mode)
        self._init_test_model()
        self.dummy_model_obj = self.env['dummy.model']
        self.thesaurus_model = self.env['thesaurus']
        self.t_model = self.env['thesaurus.term']

    def test_abstract_finder_search(self):
        # create thesaurus
        thesaurus = self.thesaurus_model.create(
            {'name': 'Beautifull Thesaurus'})

        # add thesaurus terms
        master_term_id = self.t_model.create(
            {'name': 'test value', 'thesaurus_id': thesaurus.id})
        child_term_id = self.t_model.create(
            {'name': 'test2 value', 'thesaurus_id': thesaurus.id})
        sub_child_term_id = self.t_model.create(
            {'name': 'test3 value', 'thesaurus_id': thesaurus.id})

        # master_term has a child child_term_id
        vals = {
            'child_ids': [[6, False, [child_term_id.id]]],
        }
        master_term_id.write(vals)

        # child_term_id has a parent master_term_id
        # and sub_child_term_id as a child
        vals = {
            'parent_ids': [[6, False, [master_term_id.id]]],
            'child_ids': [[6, False, [sub_child_term_id.id]]],
        }
        child_term_id.write(vals)

        # Summary of the family composition:
        # parent 1 -> master_term_id
        # first child -> child_term_id
        # parent 2 -> child_term_id
        # first child -> sub_child_term_id
        # So we have master_term_id is grandfather of sub_child_term_id
        # result : if we seek by the grandfather we must also
        # find the children

        # create dummy record
        name = 'Specific Model'
        vals = {
            'name': name,
            't_id': sub_child_term_id.id,
        }
        d_id = self.dummy_model_obj.create(vals)

        # search all dummies records using master_term_id
        domain = [('t_id', '=', master_term_id.id)]
        res_ids = self.dummy_model_obj.search(domain)
        self.assertTrue(res_ids, 'Should have a result')
        self.assertEqual(len(res_ids), 1, 'Should have 1 result')
        self.assertEqual(d_id.name, name, 'Should find with master term')

        # create another dummy record
        name = 'Specific Model 2'
        vals = {
            'name': name,
            't_id': child_term_id.id,
        }
        d_id = self.dummy_model_obj.create(vals)
        # search all records in dummyobj that have master_term_id
        domain = [('t_id', '=', master_term_id.id)]
        res_ids = self.dummy_model_obj.search(domain)
        self.assertTrue(res_ids, 'Should have a result')
        self.assertEqual(len(res_ids), 2, 'Should have 2 results')
        self.assertEqual(d_id.name, name, 'Should find with master term')

        # create another dummy record
        name = 'Specific Model 3'
        vals = {
            'name': name,
            't_id': master_term_id.id,
        }
        d_id = self.dummy_model_obj.create(vals)
        # search all records in dummyobj that have master_term_id
        domain = [('t_id', '=', master_term_id.id)]
        res_ids = self.dummy_model_obj.search(domain)
        self.assertTrue(res_ids, 'Should have a result')
        self.assertEqual(len(res_ids), 3, 'Should have 3 results')
        self.assertEqual(d_id.name, name, 'Should find with master term')
