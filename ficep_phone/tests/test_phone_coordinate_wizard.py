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
from openerp.addons.ficep_coordinate.tests.test_coordinate_wizard import test_coordinate_wizard
from anybox.testing.openerp import SharedSetupTransactionCase
import logging
_logger = logging.getLogger(__name__)


class test_phone_coordinate_wizard(test_coordinate_wizard, SharedSetupTransactionCase):

    _data_files = ('../../ficep_person/tests/data/person_data.xml',
                   'data/phone_data.xml',
                  )

    _module_ns = 'ficep_phone'

    def setUp(self):
        super(test_phone_coordinate_wizard, self).setUp()

        self.model_coordinate_wizard = self.registry('change.main.phone')
        self.model_coordinate = self.registry('phone.coordinate')
        self.model_id_1 = self.ref('%s.mobile_one' % self._module_ns)
        self.coo_into_partner = 'mobile_coordinate_id'
        self.model_coordinate_id_1 = self.ref('%s.main_mobile_coordinate_one' % self._module_ns)
        self.model_coordinate_id_2 = self.ref('%s.main_mobile_coordinate_two' % self._module_ns)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
