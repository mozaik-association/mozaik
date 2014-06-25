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


class test_membership(SharedSetupTransactionCase):

    _data_files = (
        #load the partner
        '../../ficep_base/tests/data/res_partner_data.xml',
        #load the birth_date of this partner
        '../../ficep_person/tests/data/res_partner_data.xml',
        #load email_coordinate of this partner
        '../../ficep_email/tests/data/email_data.xml',
        #load address of this partner
        '../../ficep_structure/tests/data/structure_data.xml',
        '../../ficep_address/tests/data/reference_data.xml',
        #load postal_coordinate of this partner
        '../../ficep_address/tests/data/address_data.xml',
        #load phone_coordinate of this partner
        '../../ficep_phone/tests/data/phone_data.xml',
    )

    _module_ns = 'ficep_membership'

    def setUp(self):
        super(test_membership, self).setUp()

        self.rec_partner = self.browse_ref('%s.res_partner_thierry' % self._module_ns)
        self.rec_email = self.browse_ref('%s.email_coordinate_thierry_one' % self._module_ns)
        self.rec_postal = self.browse_ref('%s.postal_coordinate_2_duplicate_2' % self._module_ns)
        self.rec_phone = self.browse_ref('%s.main_mobile_coordinate_two' % self._module_ns)

    def test_pre_process(self):
        """
        ================
        test_pre_precess
        ================
        Test that input values to create a ``membership.request``
        are found and matched with existing data
        """
        cr, uid = self.cr, self.uid

        input_values = {
            'lastname': self.rec_partner.lastname,
            'firstname': self.rec_partner.firstname,
            'gender': self.rec_partner.gender,
            'day': 1,
            'month': 04,
            'year': 1985,

            'status': 'm',
            'street': self.rec_postal.address_id.address_local_street_id.local_street,
            'zip_code': self.rec_postal.address_id.address_local_zip_id.local_zip,
            'town': self.rec_postal.address_id.address_local_zip_id.town,

            'mobile': self.rec_phone.phone_id.name,
            'email': self.rec_email.email,
        }

        output_values = self.registry('membership.request').pre_process(cr, uid, input_values)
        self.assertEqual(output_values.get('address_local_street_id', False), self.rec_postal.address_id.address_local_street_id.id, 'Should have the same street that the street of the postal coordinate')
        self.assertEqual(output_values.get('address_local_zip_id', False), self.rec_postal.address_id.address_local_zip_id.id, 'Should have the same code that the code of the postal coordinate')
        self.assertEqual(output_values.get('mobile_id', False), self.rec_phone.phone_id.id, 'Should have the same phone that the phone of the phone coordinate')
        self.assertEqual(output_values.get('partner_id', False), self.rec_partner.id, 'Should have the same partner')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
