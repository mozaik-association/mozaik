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
        self.model_coordinate_id = self.ref('%s.email_coordinate_thierry_two' % self._module_ns)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
