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
from openerp.osv import orm

import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_phone_coordinate(common.TransactionCase):

    def setUp(self):
        super(test_phone_coordinate, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        cr, uid = self.cr, self.uid
        self.model_partner = self.registry('res.partner')
        self.model_phone = self.registry('phone.phone')
        self.model_phone_coordinate = self.registry('phone.coordinate')

        self.partner_id_1 = self.model_partner.create(cr, uid, {'name': 'partner_1'}, context={})
        self.partner_id_2 = self.model_partner.create(cr, uid, {'name': 'partner_2'}, context={})
        self.partner_id_3 = self.model_partner.create(cr, uid, {'name': 'partner_3'}, context={})

        self.phone_id_1 = self.model_phone.create(cr, uid, {'name': '+32 478 85 25 25',
                                                                   'type': 'mobile'
                                                                   }, context={})
        self.phone_id_2 = self.model_phone.create(cr, uid, {'name': '+32 465 00 00 00',
                                                                   'type': 'mobile'
                                                                   }, context={})

    def test_unicity_of_phone_coordinate(self):
        """
        ================================
        test_unicity_of_phone_coordinate
        ================================
        Test the fact that the phone coordinate must be unique with
        partner_id, phone_id when no expire date
        """
        self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_1,
                                                               'is_main': True})
        self.assertRaises(orm.except_orm, self.model_phone_coordinate.create, self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                                                                  'phone_id': self.phone_id_1,
                                                                                                  'is_main': False})

    def test_create_new_main(self):
        """
        ====================
        test_create_new_main
        ====================
        Test the fact that a created phone coordinate that is main selected will
        set the previous phone coordinate to ``is_main`` = False
        **Note**
        Check also that the new is right main
        """
        pc_id_1 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_1,
                                                               'is_main': True})
        pc_id_2 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_2,
                                                               'is_main': True})
        is_main_1 = self.model_phone_coordinate.read(self.cr, self.uid, pc_id_1, ['is_main'])['is_main']
        is_main_2 = self.model_phone_coordinate.read(self.cr, self.uid, pc_id_2, ['is_main'])['is_main']
        self.assertEqual(is_main_1, False, 'Previous Phone Coordinate Should Not Be Main')
        self.assertEqual(is_main_2, True, 'New Phone Coordinate Should Be Main')

    def test_check_at_least_one_main(self):
        """
        =============================
        test_check_at_least_one_main
        =============================
        Test the fact that the associated partner of the phone coordinate has at least
        One main coordinate.
        """
        pc_id = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                                       'phone_id': self.phone_id_1,
                                                                       'is_main': False})

        is_main = self.model_phone_coordinate.read(self.cr, self.uid, [pc_id], ['is_main'])

        self.assertEqual(is_main[0]['is_main'], True, 'First Phone Coordinate Must Be Main')

    def test_set_as_main(self):
        """
        ================
        test_set_as_main
        ================
        Test the behavior of ``set_as_main``
        Context:
        phone_coo_1 : main     active
        phone_coo_2 : not main active

        Waiting result:
        phone_coo_1 : main    not active
        phone_coo_2 : main    active
        """
        pc_id_1 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_1,
                                                               'is_main': True})
        pc_id_2 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_2,
                                                               'is_main': False})
        self.model_phone_coordinate.set_as_main(self.cr, self.uid, [pc_id_2], context={'invalidate': True})

        pc_vals = self.model_phone_coordinate.read(self.cr, self.uid, [pc_id_1, pc_id_2], ['active', 'is_main'])
        mobile_coordinate_id = self.model_partner.read(self.cr, self.uid, self.partner_id_1, ['mobile_coordinate_id'])['mobile_coordinate_id']

        self.assertEqual(pc_vals[0]['is_main'] == True and
                         pc_vals[0]['active'] == False, True, 'Previous Phone Coordinate Should Be Right Invalidate')
        self.assertEqual(pc_vals[1]['is_main'] == True and
                         pc_vals[1]['active'] == True, True, 'Current Phone Coordinate Should Be New Main')
        self.assertEqual(mobile_coordinate_id[0] == pc_vals[1]['id'], True, 'Replication Failed: Should be the new selected as main phone coordinate')

    def test_bad_unlink_phone_coordinate(self):
        """
        ================================
        test_bad_unlink_phone_coordinate
        ================================
        :test_case: * creation of two phone coordinate that have the same
                          type and the same partner
                    * try to unlink the main coordinate
                    * check that is raise an ``orm.except_orm`` exception
        """
        main_phone_coordinate_id = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_1,
                                                               'is_main': True})
        self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_2,
                                                               'is_main': False})
        self.assertRaises(orm.except_orm, self.model_phone_coordinate.unlink, self.cr, self.uid, [main_phone_coordinate_id])

    def test_correct_unlink_phone_coordinate(self):
        """
        ====================================
        test_correct_unlink_phone_coordinate
        ====================================
        :test_case: * creation of two phone coordinate that have the same
                          type and the same partner
                    * try to unlink the two main coordinate
                    * check that it succeed
        """
        main_phone_coordinate_id = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_1,
                                                               'is_main': True})
        phone_coordinate_id = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                               'phone_id': self.phone_id_2,
                                                               'is_main': False})
        self.assertTrue(self.model_phone_coordinate.unlink(self.cr, self.uid, \
                         [main_phone_coordinate_id, phone_coordinate_id]), \
                         'Should be able to delete all coordinate of the same type for the same partner')

    def check_state_of_duplicate(self, is_duplicate_values, detected=None):
        for is_duplicate_value in is_duplicate_values:
            if detected is None:
                self.assertFalse(is_duplicate_value['is_duplicate_detected'], 'Should be duplicate detected')
                self.assertFalse(is_duplicate_value['is_duplicate_allowed'], 'Should not be duplicate allowed')
            else:
                if detected:
                    self.assertTrue(is_duplicate_value['is_duplicate_detected'], 'Should be duplicate detected')
                    self.assertFalse(is_duplicate_value['is_duplicate_allowed'], 'Should not be duplicate allowed')
                else:
                    self.assertTrue(is_duplicate_value['is_duplicate_allowed'], 'Should be duplicate allowed')
                    self.assertFalse(is_duplicate_value['is_duplicate_detected'], 'Should not be duplicate detected')

    def get_value_detected(self, ids):
        return self.model_phone_coordinate.read(self.cr, self.uid, ids, ['is_duplicate_detected', 'is_duplicate_allowed'],)

    def test_management_of_duplicate_create(self):
        """
        ===================================
        test_management_of_duplicate_create
        ===================================
        :test_case: * create two phone coordinate with same phone_id
                      check that ``is_duplicate_detected`` is set to True
                      check that ``is_duplicate_allowed`` is set to False
                    * allow those tow phone coordinate
                      check that ``is_duplicate_detected`` is set to False
                      check that ``is_duplicate_allowed`` is set to True
                    * create a third phone coordinate with same phone_id that previous
                      check that ``is_duplicate_detected`` is set to True
                      check that ``is_duplicate_allowed`` is set to False
        """
        coordinate_id_1 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                                                 'phone_id': self.phone_id_1}, {})
        coordinate_id_2 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_2,
                                                                                 'phone_id': self.phone_id_1}, {})
        is_duplicate_values = self.get_value_detected([coordinate_id_1, coordinate_id_2])
        self.check_state_of_duplicate(is_duplicate_values, True)

        self.model_phone_coordinate.write(self.cr, self.uid,
                                          [coordinate_id_1, coordinate_id_2],
                                          {'is_duplicate_detected': False,
                                           'is_duplicate_allowed': True})
        is_duplicate_values = self.get_value_detected([coordinate_id_1, coordinate_id_2])
        self.check_state_of_duplicate(is_duplicate_values, False)

        self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_3,
                                                                                 'phone_id': self.phone_id_1}, {})
        is_duplicate_values = self.get_value_detected([coordinate_id_1, coordinate_id_2])
        self.check_state_of_duplicate(is_duplicate_values, True)

    def test_management_of_duplicate_unlink(self):
        """
        ===================================
        test_management_of_duplicate_unlink
        ===================================
        :test_case: * create two phone coordinate with same phone_id
                    * allow those tow phone coordinate
                    * unlink on of those coordinate
                      check that ``is_duplicate_detected`` is set to False
                      check that ``is_duplicate_allowed`` is set to False
        """
        coordinate_id_1 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                                                 'phone_id': self.phone_id_1}, {})
        coordinate_id_2 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_2,
                                                                                 'phone_id': self.phone_id_1}, {})
        self.model_phone_coordinate.unlink(self.cr, self.uid, [coordinate_id_2])
        is_duplicate_values = self.get_value_detected([coordinate_id_1])
        self.check_state_of_duplicate(is_duplicate_values)

    def test_management_of_duplicate_invalidate(self):
        """
        =======================================
        test_management_of_duplicate_invalidate
        =======================================
        :test_case: * create two phone coordinate with same phone_id
                    * allow those tow phone coordinate
                    * invalidate first coordinate
                      check that the active one ``is_duplicate_detected`` is set to False
                      check that the active one ``is_duplicate_allowed`` is set to False
        """
        coordinate_id_1 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_1,
                                                                                 'phone_id': self.phone_id_1}, {})
        coordinate_id_2 = self.model_phone_coordinate.create(self.cr, self.uid, {'partner_id': self.partner_id_2,
                                                                                 'phone_id': self.phone_id_1}, {})
        self.model_phone_coordinate.button_invalidate(self.cr, self.uid, [coordinate_id_2])
        is_duplicate_values = self.get_value_detected([coordinate_id_1])
        self.check_state_of_duplicate(is_duplicate_values)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
