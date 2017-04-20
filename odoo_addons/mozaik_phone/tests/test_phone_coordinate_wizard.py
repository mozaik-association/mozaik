# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_phone, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_phone is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_phone is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_phone.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.mozaik_coordinate.tests.test_coordinate_wizard import \
    test_coordinate_wizard
from anybox.testing.openerp import SharedSetupTransactionCase
import logging
_logger = logging.getLogger(__name__)


class test_phone_coordinate_wizard(
        test_coordinate_wizard,
        SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        'data/phone_data.xml',
    )

    _module_ns = 'mozaik_phone'

    def setUp(self):
        super(test_phone_coordinate_wizard, self).setUp()

        # instanciated members of abstract test
        self.model_coordinate_wizard = self.registry('change.main.phone')
        self.model_coordinate = self.registry('phone.coordinate')
        self.model_id_1 = self.ref('%s.mobile_one' % self._module_ns)
        self.coo_into_partner = 'mobile_coordinate_id'
        self.model_coordinate_id_1 = self.ref(
            '%s.main_mobile_coordinate_one' %
            self._module_ns)
        self.model_coordinate_id_2 = self.ref(
            '%s.main_mobile_coordinate_two' %
            self._module_ns)
        self.field_id_1 = self.ref('%s.mobile_one' % self._module_ns)
        self.field_id_2 = self.ref('%s.mobile_two' % self._module_ns)
