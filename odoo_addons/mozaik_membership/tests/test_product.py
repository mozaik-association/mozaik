# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from anybox.testing.openerp import SharedSetupTransactionCase


_logger = logging.getLogger(__name__)


class test_product(SharedSetupTransactionCase):

    _module_ns = 'mozaik_membership'

    def setUp(self):
        super(test_product, self).setUp()

        self.model_product = self.registry('product.template')

    def test_get_default_subscription(self):
        """
        Test that there is a default subscription.
        Required for right behavior of the request membership management
        """
        cr, uid, context = self.cr, self.uid, {}
        default_id = self.model_product._get_default_subscription(
            cr, uid, context=context)
        self.assertTrue(default_id, "Seems like 'default subscription' product\
            has been deleting")
