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
from anybox.testing.openerp import SharedSetupTransactionCase
import logging
_logger = logging.getLogger(__name__)


class test_phone_coordinate_wizard(SharedSetupTransactionCase):

    _data_files = ('../../ficep_person/tests/data/person_data.xml',
                   'data/phone_data.xml',
                  )

    _module_ns = 'ficep_phone'

    def setUp(self):
        super(test_phone_coordinate_wizard, self).setUp()

        self.model_partner = self.registry('res.partner')
        self.model_phone = self.registry('phone.phone')
        self.model_phone_coordinate = self.registry('phone.coordinate')

        self.partner_id_1 = self.ref('%s.res_partner_pauline' % self._module_ns)
        self.phone_id_2 = self.ref('%s.fix_for_test_update_2' % self._module_ns)
        self.phone_coordinate_id_1 = self.ref('%s.phone_coo_for_test_update_1' % self._module_ns)

    def test_create_phone_coordinate(self):
        """
        ============================
        test_create_phone_coordinate
        ============================
        Test the fact that when a phone_coordinate is create for a partner,
        The phone value is right set
        """
        partner_value = self.model_partner.read(self.cr, self.uid, self.partner_id_1, ['phone'], context={})
        phone_value = self.model_phone_coordinate.browse(self.cr, self.uid, self.phone_coordinate_id_1, context={}).phone_id.name
        self.assertEqual(partner_value['phone'] == phone_value, True, "Phone Should Be Set With The Same Value")

    def test_update_phone_coordinate(self):
        """
        ============================
        test_update_phone_coordinate
        ============================
        Test the fact that when a phone_id is updated for a phone_coordinate
        The phone value is right set for the partner of this phone_coordinate
        """
        self.model_phone_coordinate.write(self.cr, self.uid, self.phone_coordinate_id_1, {'phone_id': self.phone_id_2}, context={})
        partner_value = self.model_partner.read(self.cr, self.uid, self.partner_id_1, ['phone'], context={})
        phone_value = self.model_phone_coordinate.browse(self.cr, self.uid, self.phone_coordinate_id_1, context={}).phone_id.name
        self.assertEqual(partner_value['phone'] == phone_value, True, "Phone Should Be Set With The Same Value")

    def test_update_phone_number(self):
        """
        ========================
        test_update_phone_number
        ========================
        Test the fact that when a number is updated for a phone_coordinate that
        is associated with a partner, the phone value is right set for the
        partner of this phone_coordinate
        """
        self.model_phone_coordinate.write(self.cr, self.uid, self.phone_coordinate_id_1, {'phone_id': self.phone_id_2}, context={})
        self.model_phone.write(self.cr, self.uid, self.phone_id_2, {'name': '091452325'}, context={})
        partner_value = self.model_partner.read(self.cr, self.uid, self.partner_id_1, ['phone'], context={})
        phone_value = self.model_phone_coordinate.browse(self.cr, self.uid, self.phone_coordinate_id_1, context={}).phone_id.name
        self.assertEqual(partner_value['phone'] == phone_value, True, "Phone Should Be Set With The Same Value")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
