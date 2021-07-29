# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo.tests.common import TransactionCase


_logger = logging.getLogger(__name__)


class TestProduct(TransactionCase):

    def setUp(self):
        super().setUp()
        self.model_product = self.env['product.template']

    def test_get_default_subscription(self):
        """
        Test that there is a default subscription.
        Required for right behavior of the request membership management
        """
        default_id = self.model_product._get_default_subscription()
        self.assertTrue(default_id, "Seems like 'default subscription' product\
            has been deleting")
