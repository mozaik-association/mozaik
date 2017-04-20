# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_email, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_email is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_email is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_email.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.mozaik_coordinate.tests.test_bounce import test_bounce
from anybox.testing.openerp import SharedSetupTransactionCase


class test_email_bounce(test_bounce, SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        'data/email_data.xml',
    )

    _module_ns = 'mozaik_email'

    def setUp(self):
        super(test_email_bounce, self).setUp()

        # instanciate members of abstract test
        self.model_coordinate = self.registry('email.coordinate')
        self.model_coordinate_id = self.ref(
            '%s.email_coordinate_thierry_two' % self._module_ns)
