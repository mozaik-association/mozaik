# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from uuid import uuid4
import odoo
from odoo.tests.common import TransactionCase
from odoo import fields, models
from .common_mozaik_abstract_model import CommonMozaikAbstractModel


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = [
        'mozaik.abstract.model',
        'res.partner',
    ]
    _inactive_cascade = True
    _unicity_keys = 'N/A'


class TestChildModel(models.Model):
    _name = 'test.child.model'
    _inherit = [
        'mozaik.abstract.model',
    ]
    _description = "Test child model"
    _unicity_keys = 'N/A'

    name = fields.Char(
        required=True,
    )
    partner_id = fields.Many2one(
        ResPartner._name,
        "Partner",
        required=True,
    )


class TestMozaikAbstractModel(CommonMozaikAbstractModel, TransactionCase):
    """
    Tests for mozaik.abstract.model
    """

    def _get_odoo_models(self):
        """
        Get Odoo models to update/instantiate
        :return: list
        """
        return [TestChildModel, ResPartner, TestAnotherModel]

    def _get_odoo_models_exist(self):
        """
        Get existing Odoo models to update/instantiate
        :return: list
        """
        return [ResPartner]

    def _init_test_models(self):
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
        registry = odoo.registry()
        registry_fields = {}
        for OdooModel in self._get_odoo_models_exist():
            registry_fields.update({
                OdooModel._name: set(registry[OdooModel._name]._fields)
            })
        super(TestMozaikAbstractModel, self).setUp()

        @self.addCleanup
        def reset():
            # reset registry and env
            registry._clear_cache()
            registry.clear_caches()
            registry.reset_changes()
            self.env.reset()
        # We must be in test mode before create/init new models
        registry.enter_test_mode()
        # Add the cleanup to disable test mode after this setup as finished
        self.addCleanup(registry.leave_test_mode)
        self._init_test_models()
        # Concrete Odoo models who inherit mozaik.abstract.model
        self.implemented_mozaik_abstract_obj = self.env[
            ResPartner._name]
        # Odoo model with _inactive_cascade = True to disable records
        self.child_obj = self.env[TestChildModel._name]
        self.trigger1 = self.implemented_mozaik_abstract_obj.create({
            'name': str(uuid4()),
            'email': '%s@example.test' % str(uuid4()),
        })
        self.child1 = self.child_obj.create({
            'partner_id': self.trigger1.id,
            'name': str(uuid4()),
        })
        self.child2 = self.child_obj.create({
            'partner_id': self.trigger1.id,
            'name': str(uuid4()),
        })

    def test_no_infinite_loop1(self):
        """
        For this case, we ensure that we won't have any infinite loop
        when the child have the same model than the 'master'.
        Example with res.partner and related contacts
        :return: bool
        """
        self.child1 = self.implemented_mozaik_abstract_obj.create({
            'name': str(uuid4()),
            'email': '%s@example.test' % str(uuid4()),
            'parent_id': self.trigger1.id,
        })
        self.child2 = self.implemented_mozaik_abstract_obj.create({
            'name': str(uuid4()),
            'email': '%s@example.test' % str(uuid4()),
            'parent_id': self.trigger1.id,
        })
        self.test_disable_cascade1()
        return True

    def test_no_infinite_loop2(self):
        """
        For this case, we ensure that we won't have any infinite loop
        when the child have the same model than the 'master'.
        Example with res.partner and related contacts
        :return: bool
        """
        self.child1 = self.implemented_mozaik_abstract_obj.create({
            'name': str(uuid4()),
            'email': '%s@example.test' % str(uuid4()),
            'parent_id': self.trigger1.id,
        })
        self.child2 = self.implemented_mozaik_abstract_obj.create({
            'name': str(uuid4()),
            'email': '%s@example.test' % str(uuid4()),
            'parent_id': self.trigger1.id,
        })
        self.test_disable_cascade2()
        return True
