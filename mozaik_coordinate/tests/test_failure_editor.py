# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from uuid import uuid4
from odoo.tests.common import TransactionCase
from .common_failure_editor import CommonFailureEditor
from .test_abstract_coordinate import ResPartner, NotAbstractCoordinate

DESC = "Bad Coordinate"


class TestCommonFailureEditor(CommonFailureEditor, TransactionCase):
    """
    Run test for the abstract class too
    resolved with a dual inherit on the abstract and the common.NAME
    """

    def _get_odoo_models(self):
        """
        Inherit to add a new model to instantiate
        :return: list of Odoo Models
        """
        return [ResPartner, NotAbstractCoordinate]

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
        super(TestCommonFailureEditor, self).setUp()
        registry = self.env.registry
        # We must be in test mode before create/init new models
        registry.enter_test_mode(self.env.cr)
        # Add the cleanup to disable test mode after this setup as finished
        self.addCleanup(self.registry.leave_test_mode)
        self._init_test_models()
        self.model_coordinate = self.env[NotAbstractCoordinate._name]
        self.coo_into_partner = "not_abstract_coordinate_id"
        self.coordinate = self.model_coordinate.create(
            {
                "name": str(uuid4()),
                "partner_id": self.partner1.id,
                self.model_coordinate._discriminant_field: str(uuid4()),
            }
        )
