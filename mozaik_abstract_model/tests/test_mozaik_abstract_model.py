# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from uuid import uuid4

from odoo import fields, models
from odoo.tests.common import TransactionCase

from .common_mozaik_abstract_model import CommonMozaikAbstractModel

test_partner_name = "test.res.partner"


class TestResPartner(models.Model):
    _name = test_partner_name
    _inherit = "mozaik.abstract.model"
    _inactive_cascade = True
    _unicity_keys = "N/A"
    _abstract = True
    _description = "Test Res Partner"

    name = fields.Char()
    email = fields.Char()
    parent_id = fields.Many2one(
        test_partner_name,
    )
    child_ids = fields.One2many(
        test_partner_name,
        "parent_id",
    )


class TestChildModel(models.Model):
    _name = "test.child.model"
    _inherit = [
        "mozaik.abstract.model",
    ]
    _description = "Test child model"
    _unicity_keys = "N/A"
    _abstract = True

    name = fields.Char(
        required=True,
    )
    partner_id = fields.Many2one(
        TestResPartner._name,
        "Partner",
        required=True,
    )


class TestAnotherModel(models.Model):
    """
    Model who doesn't implements mozaik.abstract.model for the following
    tests
    """

    _name = "test.another.model"
    _description = "Test another model"
    _unicity_keys = "N/A"
    _abstract = True

    name = fields.Char(
        required=True,
    )
    partner_id = fields.Many2one(
        TestResPartner._name,
        "Partner",
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )

    def write(self, vals):
        """
        For this test, whatever is set into the active field, we set it to
        True (to disable inactivation)
        :param vals: dict
        :return: bool
        """
        vals.update(
            {
                "active": True,
            }
        )
        return super().write(vals)


class TestMozaikAbstractModel(CommonMozaikAbstractModel, TransactionCase):
    """
    Tests for mozaik.abstract.model
    """

    def _get_odoo_models(self):
        """
        Get Odoo models to update/instantiate
        Order is important
        :return: list
        """
        return [TestResPartner, TestChildModel, TestAnotherModel]

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
        super().setUp()
        registry = self.registry
        # We must be in test mode before create/init new models
        registry.enter_test_mode(self.env.cr)
        # Add the cleanup to disable test mode after this setup as finished
        self.addCleanup(registry.leave_test_mode)
        self._init_test_models()
        # Concrete Odoo models who inherit mozaik.abstract.model
        self.implemented_mozaik_abstract_obj = self.env[TestResPartner._name]
        # Odoo model with _inactive_cascade = True to disable records
        self.child_obj = self.env[TestChildModel._name]
        self.trigger1 = self.implemented_mozaik_abstract_obj.create(
            {
                "name": str(uuid4()),
                "email": "%s@example.test" % str(uuid4()),
            }
        )
        self.child1 = self.child_obj.create(
            {
                "partner_id": self.trigger1.id,
                "name": str(uuid4()),
            }
        )
        self.child2 = self.child_obj.create(
            {
                "partner_id": self.trigger1.id,
                "name": str(uuid4()),
            }
        )
        self.invalidate_success = self.trigger1
        partner_invalid_fails = self.trigger1.copy()
        invalidate_obj = self.env[TestAnotherModel._name]
        partner_invalid_fails.write(
            {
                "expire_date": fields.Date.today(),
            }
        )
        invalidate_obj.create(
            {
                "name": str(uuid4()),
                "partner_id": partner_invalid_fails.id,
                "active": True,
            }
        )
        self.invalidate_fails = partner_invalid_fails
        self.validates = self.trigger1

    def test_no_infinite_loop1(self):
        """
        For this case, we ensure that we won't have any infinite loop
        when the child have the same model than the 'master'.
        Example with test.res.partner and related contacts
        :return: bool
        """
        self.child1 = self.implemented_mozaik_abstract_obj.create(
            {
                "name": str(uuid4()),
                "email": "%s@example.test" % str(uuid4()),
                "parent_id": self.trigger1.id,
            }
        )
        self.child2 = self.implemented_mozaik_abstract_obj.create(
            {
                "name": str(uuid4()),
                "email": "%s@example.test" % str(uuid4()),
                "parent_id": self.trigger1.id,
            }
        )
        self.test_disable_cascade1()
        return True

    def test_no_infinite_loop2(self):
        """
        For this case, we ensure that we won't have any infinite loop
        when the child have the same model than the 'master'.
        Example with test.res.partner and related contacts
        :return: bool
        """
        self.child1 = self.implemented_mozaik_abstract_obj.create(
            {
                "name": str(uuid4()),
                "email": "%s@example.test" % str(uuid4()),
                "parent_id": self.trigger1.id,
            }
        )
        self.child2 = self.implemented_mozaik_abstract_obj.create(
            {
                "name": str(uuid4()),
                "email": "%s@example.test" % str(uuid4()),
                "parent_id": self.trigger1.id,
            }
        )
        self.test_disable_cascade2()
        return True
