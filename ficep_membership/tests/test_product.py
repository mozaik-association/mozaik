# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from anybox.testing.openerp import SharedSetupTransactionCase


_logger = logging.getLogger(__name__)


class test_product(SharedSetupTransactionCase):

    _module_ns = 'ficep_membership'

    def setUp(self):
        super(test_product, self).setUp()

        self.model_product = self.registry('product.template')

    def test_get_default_subscription(self):
        """
        =============================
        test_get_default_subscription
        =============================
        Test that there is a default subscription.
        Required for right behavior of the request membership management
        """
        cr, uid, context = self.cr, self.uid, {}
        default_id = self.model_product._get_default_subscription(cr, uid, context=context)
        self.assertTrue(default_id, "Seems like 'default subscription' product has been deleting")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
