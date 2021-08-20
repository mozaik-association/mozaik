# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from uuid import uuid4
from odoo import models, fields
from odoo.tests.common import TransactionCase
from .common_coordinate_wizard import CommonCoordinateWizard
from .test_abstract_coordinate import ResPartner, NotAbstractCoordinate


class TestChangeMainCoordinate(models.Model):
    """
    A concrete Odoo Wizard used for these tests only
    """

    _description = "Test change main coordinate"
    _name = "test.change.main.coordinate"
    _inherit = ["change.main.coordinate"]
    _abstract = True

    discr_field = fields.Char()


class TestCoordinateWizard(CommonCoordinateWizard, TransactionCase):
    def _get_odoo_models(self):
        """
        Inherit to add a new model to instantiate
        :return: list of Odoo Models
        """
        return [TestChangeMainCoordinate, ResPartner, NotAbstractCoordinate]

    def _init_test_models(self):
        """
        Function to init/create a new Odoo Model during unit test.
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
        return

    def setUp(self):
        super(TestCoordinateWizard, self).setUp()
        registry = self.env.registry
        # We must be in test mode before create/init new models
        registry.enter_test_mode(self.env.cr)
        # Add the cleanup to disable test mode after this setup as finished
        self.addCleanup(self.registry.leave_test_mode)
        self._init_test_models()
        self.model_coordinate_wizard = self.env[TestChangeMainCoordinate._name]
        self.model_coordinate = self.env[NotAbstractCoordinate._name]
        self.coo_into_partner = "not_abstract_coordinate_id"
        self.coordinate1 = self.model_coordinate.create(
            {
                "name": str(uuid4()),
                "partner_id": self.partner1.id,
                self.model_coordinate._discriminant_field: str(uuid4()),
            }
        )
        self.coordinate2 = self.model_coordinate.create(
            {
                "name": str(uuid4()),
                "partner_id": self.partner2.id,
                self.model_coordinate._discriminant_field: str(uuid4()),
            }
        )
