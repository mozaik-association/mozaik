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
from anybox.testing.openerp import SharedSetupTransactionCase
import logging
_logger = logging.getLogger(__name__)


class testChangePhoneType(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        'data/phone_data.xml',
    )

    _module_ns = 'mozaik_phone'

    def setUp(self):
        super(testChangePhoneType, self).setUp()
        self.env.invalidate_all()
        self.mobile_four = self.browse_ref('%s.mobile_four'
                                           % self._module_ns)
        self.mobile_five = self.browse_ref('%s.mobile_five'
                                           % self._module_ns)
        self.fix_one = self.browse_ref('%s.fix_one'
                                       % self._module_ns)
        self.fix_two = self.browse_ref('%s.fix_two'
                                       % self._module_ns)
        self.coord_mobile_1 = self.browse_ref(
            '%s.mobile_coordinate_for_jacques_1' % self._module_ns)
        self.coord_mobile_2 = self.browse_ref(
            '%s.mobile_coordinate_for_jacques_2' % self._module_ns)
        self.coord_fix_1 = self.browse_ref('%s.fix_coordinate_for_jacques_1'
                                           % self._module_ns)
        self.coord_fix_2 = self.browse_ref('%s.fix_coordinate_for_jacques_2'
                                           % self._module_ns)
        self.wiz_obj = self.env['change.phone.type']

    def test_change_main_mobile_to_fix_main(self):
        '''
            Trying to change mobile_four (main) from mobile to fix and
            set is as main in the new category.
            Expected results are:
            - mobile_four type should be FIX
            - mobile_coordinate_for_jacques_1 type should be FIX and MAIN
            - mobile_coordinate_for_jacques_2 should become main
            - fix_coordinate_for_jacques_1 should not be main anymore
        '''
        wiz = self.wiz_obj.create({'phone_id': self.mobile_four.id,
                                   'type': 'fix'})
        wiz.change_phone_type()
        self.env.invalidate_all()
        self.assertEqual(self.mobile_four.type, 'fix')
        self.assertEqual(self.coord_mobile_1.coordinate_type, 'fix')
        self.assertTrue(self.coord_mobile_2.is_main)
        self.assertTrue(self.coord_mobile_1.is_main)
        self.assertFalse(self.coord_fix_1.is_main)

    def test_change_main_mobile_to_fix_no_main(self):
        '''
            Trying to change mobile_four (main) from mobile to fix but
            do not set it as main in the new category.
            Expected results are:
            - mobile_four type should be FIX
            - mobile_coordinate_for_jacques_1 type should be FIX and not MAIN
            - mobile_coordinate_for_jacques_2 should become main
            - fix_coordinate_for_jacques_1 should be main anymore
        '''
        wiz = self.wiz_obj.create({'phone_id': self.mobile_four.id,
                                   'type': 'fix',
                                   'is_main': False})
        wiz.change_phone_type()
        self.env.invalidate_all()
        self.assertEqual(self.mobile_four.type, 'fix')
        self.assertEqual(self.coord_mobile_1.coordinate_type, 'fix')
        self.assertTrue(self.coord_mobile_2.is_main)
        self.assertFalse(self.coord_mobile_1.is_main)
        self.assertTrue(self.coord_fix_1.is_main)

    def test_change_not_main_mobile_to_fix_main(self):
        '''
            Trying to change mobile_five (not main) from mobile to fix and
            set is as main in the new category.
            Expected results are:
            - mobile_five type should be FIX
            - mobile_coordinate_for_jacques_2 type should be FIX and MAIN
            - mobile_coordinate_for_jacques_1 should remain main
            - fix_coordinate_for_jacques_1 should not be main anymore
        '''
        wiz = self.wiz_obj.create({'phone_id': self.mobile_five.id,
                                   'type': 'fix'})
        wiz.change_phone_type()
        self.env.invalidate_all()
        self.assertEqual(self.mobile_five.type, 'fix')
        self.assertEqual(self.coord_mobile_2.coordinate_type, 'fix')
        self.assertTrue(self.coord_mobile_1.is_main)
        self.assertTrue(self.coord_mobile_2.is_main)
        self.assertFalse(self.coord_fix_1.is_main)

    def test_change_not_main_mobile_to_fix_no_main(self):
        '''
            Trying to change mobile_five (not main) from mobile to fix and
            do not set is as main in the new category.
            Expected results are:
            - mobile_five type should be FIX
            - mobile_coordinate_for_jacques_2 type should be FIX and should
              remain not main
            - mobile_coordinate_for_jacques_1 should remain main
            - fix_coordinate_for_jacques_1 should remain main
        '''
        wiz = self.wiz_obj.create({'phone_id': self.mobile_five.id,
                                   'type': 'fix',
                                   'is_main': False})
        wiz.change_phone_type()
        self.env.invalidate_all()
        self.assertEqual(self.mobile_five.type, 'fix')
        self.assertEqual(self.coord_mobile_2.coordinate_type, 'fix')
        self.assertTrue(self.coord_mobile_1.is_main)
        self.assertFalse(self.coord_mobile_2.is_main)
        self.assertTrue(self.coord_fix_1.is_main)
