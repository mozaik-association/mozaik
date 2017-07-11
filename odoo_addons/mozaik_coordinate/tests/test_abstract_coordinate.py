# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import psycopg2

from openerp.osv import orm

from openerp.addons.mozaik_base import testtool


class abstract_coordinate(object):
    """ unittest2 run test for the abstract class too
    resolved with a dual inherit on the abstract and the common.NAME
    """

    def setUp(self):
        super(abstract_coordinate, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        cr, uid = self.cr, self.uid
        self.model_partner = self.registry('res.partner')

        self.partner_id_1 = self.model_partner.create(
            cr, uid, {'name': 'partner_1'}, context={})
        self.partner_id_2 = self.model_partner.create(
            cr, uid, {'name': 'partner_2'}, context={})
        self.partner_id_3 = self.model_partner.create(
            cr, uid, {'name': 'partner_3'}, context={})

        # members to instanciate by real test
        self.model_coordinate = None
        self.field_id_1 = None
        self.field_id_2 = None
        self.coo_into_partner = None

    def test_unicity_of_abstract_coordinate(self):
        """
        ===================================
        test_unicity_of_abstract_coordinate
        ===================================
        Test the fact that the model coordinate must be unique with
        partner_id, model_id when no expire date
        """
        self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1,
             'is_main': True})
        with testtool.disable_log_error(self.cr):
            self.assertRaises(
                psycopg2.IntegrityError,
                self.model_coordinate.create,
                self.cr, self.uid,
                {'partner_id': self.partner_id_1,
                 self.model_coordinate._discriminant_field: self.field_id_1,
                 'is_main': False,
                 })

    def test_create_new_main(self):
        """
        ====================
        test_create_new_main
        ====================
        Test the fact that a created model coordinate that is main selected
        will set the previous model coordinate to ``is_main`` = False
        **Note**
        Check also that the new is right main
        """
        pc_id_1 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1,
             'is_main': True})
        pc_id_2 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_2,
             'is_main': True})
        is_main_1 = self.model_coordinate.read(
            self.cr, self.uid, pc_id_1, ['is_main'])['is_main']
        is_main_2 = self.model_coordinate.read(
            self.cr, self.uid, pc_id_2, ['is_main'])['is_main']
        self.assertEqual(
            is_main_1, False, 'Previous model Coordinate Should Not Be Main')
        self.assertEqual(
            is_main_2, True, 'New model Coordinate Should Be Main')

    def test_check_at_least_one_main(self):
        """
        =============================
        test_check_at_least_one_main
        =============================
        Test the fact that the associated partner of the model coordinate has
        at least one main coordinate.
        """
        pc_id = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1,
             'is_main': False})

        is_main = self.model_coordinate.read(
            self.cr, self.uid, [pc_id], ['is_main'])

        self.assertEqual(is_main[0]['is_main'], True,
                         'First model Coordinate Must Be Main')

    def test_set_as_main(self):
        """
        ================
        test_set_as_main
        ================
        Test the behavior of ``set_as_main``
        Context:
        model_coo_1 : main     active
        model_coo_2 : not main active

        Waiting result:
        model_coo_1 : main    not active
        model_coo_2 : main    active
        """
        pc_id_1 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1,
             'is_main': True})
        pc_id_2 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_2,
             'is_main': False})
        self.model_coordinate.set_as_main(
            self.cr, self.uid, [pc_id_2], context={'invalidate': True})

        pc_vals = self.model_coordinate.read(
            self.cr, self.uid, [pc_id_1, pc_id_2], ['active', 'is_main'])
        coordinate_id = self.model_partner.read(
            self.cr, self.uid, self.partner_id_1,
            [self.coo_into_partner])[self.coo_into_partner]

        self.assertTrue(
            pc_vals[0]['is_main'] and not pc_vals[0]['active'],
            'Previous model Coordinate Should Be Right Invalidate')
        self.assertTrue(pc_vals[1]['is_main'] and pc_vals[1]['active'],
                        'Current model Coordinate Should Be New Main')
        self.assertTrue(
            coordinate_id[0] == pc_vals[1]['id'],
            'Replication Failed: Should be the new selected as main model '
            'coordinate')

    def test_bad_unlink_abstract_coordinate(self):
        """
        ===================================
        test_bad_unlink_abstract_coordinate
        ===================================
        :test_case: * creation of two model coordinate that have the same
                          type and the same partner
                    * try to unlink the main coordinate
                    * check that is raise an ``orm.except_orm`` exception
        """
        main_abstract_coordinate_id = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1,
             'is_main': True})
        self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_2,
             'is_main': False})
        self.assertRaises(
            orm.except_orm,
            self.model_coordinate.unlink, self.cr, self.uid,
            [main_abstract_coordinate_id])

    def test_correct_unlink_abstract_coordinate(self):
        """
        =======================================
        test_correct_unlink_abstract_coordinate
        =======================================
        :test_case: * creation of two model coordinate that have the same
                          type and the same partner
                    * try to unlink the two main coordinate
                    * check that it succeed
        """
        main_abstract_coordinate_id = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1,
             'is_main': True})
        abstract_coordinate_id = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_2,
             'is_main': False})
        self.assertTrue(
            self.model_coordinate.unlink(
                self.cr, self.uid,
                [main_abstract_coordinate_id, abstract_coordinate_id]),
            'Should be able to delete all coordinate of the same type for the '
            'same partner')

    def check_state_of_duplicate(self, is_duplicate_values, detected=None):
        for is_duplicate_value in is_duplicate_values:
            if detected is None:
                self.assertFalse(
                    is_duplicate_value['is_duplicate_detected'],
                    'Should be duplicate detected')
                self.assertFalse(
                    is_duplicate_value['is_duplicate_allowed'],
                    'Should not be duplicate allowed')
            else:
                if detected:
                    self.assertTrue(
                        is_duplicate_value['is_duplicate_detected'],
                        'Should be duplicate detected')
                    self.assertFalse(
                        is_duplicate_value['is_duplicate_allowed'],
                        'Should not be duplicate allowed')
                else:
                    self.assertTrue(
                        is_duplicate_value['is_duplicate_allowed'],
                        'Should be duplicate allowed')
                    self.assertFalse(
                        is_duplicate_value['is_duplicate_detected'],
                        'Should not be duplicate detected')

    def get_value_detected(self, ids):
        return self.model_coordinate.read(
            self.cr, self.uid, ids,
            ['is_duplicate_detected', 'is_duplicate_allowed'])

    def test_management_of_duplicate_create(self):
        """
        ===================================
        test_management_of_duplicate_create
        ===================================
        :test_case: * create two model coordinate with same model_id
                      check that ``is_duplicate_detected`` is set to True
                      check that ``is_duplicate_allowed`` is set to False
                    * allow those tow model coordinate
                      check that ``is_duplicate_detected`` is set to False
                      check that ``is_duplicate_allowed`` is set to True
                    * create a third model coordinate with same model_id than
                      previous
                      check that ``is_duplicate_detected`` is set to True
                      check that ``is_duplicate_allowed`` is set to False
        """
        coordinate_id_1 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1}, {})
        coordinate_id_2 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_2,
             self.model_coordinate._discriminant_field: self.field_id_1}, {})
        is_duplicate_values = self.get_value_detected(
            [coordinate_id_1, coordinate_id_2])
        self.check_state_of_duplicate(is_duplicate_values, True)

        self.model_coordinate.write(
            self.cr, self.uid,
            [coordinate_id_1, coordinate_id_2],
            {'is_duplicate_detected': False,
             'is_duplicate_allowed': True})
        is_duplicate_values = self.get_value_detected(
            [coordinate_id_1, coordinate_id_2])
        self.check_state_of_duplicate(is_duplicate_values, False)

        self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_3,
             self.model_coordinate._discriminant_field: self.field_id_1}, {})
        is_duplicate_values = self.get_value_detected(
            [coordinate_id_1, coordinate_id_2])
        self.check_state_of_duplicate(is_duplicate_values, True)

    def test_management_of_duplicate_unlink(self):
        """
        ===================================
        test_management_of_duplicate_unlink
        ===================================
        :test_case: * create two model coordinate with same model_id
                    * allow those tow model coordinate
                    * unlink on of those coordinate
                      check that ``is_duplicate_detected`` is set to False
                      check that ``is_duplicate_allowed`` is set to False
        """
        coordinate_id_1 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1}, {})
        coordinate_id_2 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_2,
             self.model_coordinate._discriminant_field: self.field_id_1}, {})
        self.model_coordinate.unlink(self.cr, self.uid, [coordinate_id_2])
        is_duplicate_values = self.get_value_detected([coordinate_id_1])
        self.check_state_of_duplicate(is_duplicate_values)

    def test_management_of_duplicate_invalidate(self):
        """
        =======================================
        test_management_of_duplicate_invalidate
        =======================================
        :test_case: * create two model coordinate with same model_id
                    * allow those tow model coordinate
                    * invalidate first coordinate
                      check that the active one ``is_duplicate_detected`
                           is set to False
                      check that the active one ``is_duplicate_allowed``
                          is set to False
        """
        coordinate_id_1 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_1,
             self.model_coordinate._discriminant_field: self.field_id_1}, {})
        coordinate_id_2 = self.model_coordinate.create(
            self.cr, self.uid,
            {'partner_id': self.partner_id_2,
             self.model_coordinate._discriminant_field: self.field_id_1}, {})
        self.model_coordinate.action_invalidate(
            self.cr, self.uid, [coordinate_id_2])
        is_duplicate_values = self.get_value_detected([coordinate_id_1])
        self.check_state_of_duplicate(is_duplicate_values)

    def test_bad_invalidate(self):
        """
        :test_case: * create three models coordinate with same model_id for the
                        same partner
                    * invalidate main coordinate
                    * check that it fails
        """
        cr, uid, context = self.cr, self.uid, {}
        vals = {
            'partner_id': self.partner_id_1,
            self.model_coordinate._discriminant_field: self.field_id_1,
        }
        coordinate_id_1 = self.model_coordinate.create(
            cr, uid, vals, context=context)
        vals = {
            'partner_id': self.partner_id_1,
            self.model_coordinate._discriminant_field: self.field_id_2,
        }
        self.model_coordinate.create(
            cr, uid, vals, context=context)
        vals = {
            'partner_id': self.partner_id_1,
            self.model_coordinate._discriminant_field: self.field_id_3,
        }
        self.model_coordinate.create(
            cr, uid, vals, context=context)
        self.assertRaises(orm.except_orm,
                          self.model_coordinate.action_invalidate, cr, uid,
                          [coordinate_id_1], context=context)

    def test_autoswitch_main_on_invalidate(self):
        """
        :test_case: * create 2 models coordinate with same model_id for the
                        same partner
                    * invalidate main coordinate
                    * check if the second one is now the main coordinate
        """
        cr, uid, context = self.cr, self.uid, {}
        vals = {
            'partner_id': self.partner_id_1,
            self.model_coordinate._discriminant_field: self.field_id_1,
        }
        coordinate_id_1 = self.model_coordinate.create(
            cr, uid, vals, context=context)
        vals = {
            'partner_id': self.partner_id_1,
            self.model_coordinate._discriminant_field: self.field_id_2,
        }
        coordinate_id_2 = self.model_coordinate.create(
            cr, uid, vals, context=context)

        self.model_coordinate.action_invalidate(cr, uid,
                                                [coordinate_id_1],
                                                context=context)
        coordinate = self.model_coordinate.browse(cr, uid,
                                                  coordinate_id_2,
                                                  context=context)
        self.assertTrue(coordinate.is_main)
