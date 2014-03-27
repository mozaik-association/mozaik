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
from anybox.testing.openerp import SharedSetupTransactionCase
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_postal_coordinate(SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        'data/reference_data.xml',
        'data/address_data.xml',
    )

    _module_ns = 'ficep_address'

    def setUp(self):
        super(test_postal_coordinate, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        self.allow_duplicate_wizard_model = self.registry('allow.duplicate.wizard')
        self.postal_model = 'postal.coordinate'

    def test_check_co_residency_consistency(self):
        postal_coo_2 = self.ref("ficep_address.postal_coordinate_2")
        postal_coo_3 = self.ref("ficep_address.postal_coordinate_3")
        co_residency = self.ref("ficep_address.co_residency_id_1")
        self.assertRaises(orm.except_orm, self.registry('postal.coordinate').write,
                                          self.cr, ADMIN_USER_ID,
                                          [postal_coo_3, postal_coo_2],
                                          {'co_residency_id': co_residency})

    def test_all_duplicate_co_residency(self):
        """
        ===============================
        test_all_duplicate_co_residency
        ===============================
        Test requirement:
        4 duplicate postal coordinates
        2 co-residencies
        Test Case:
        1) Allow 2 duplicate postal coordinates with one co-residency
            * Check the 2 are now duplicate allowed
            * Check the 2 are no more duplicate detected
            * Check the 2 are associated with the co-residency
        2) Try Allow 1 of the two other with the second co-residency
            * Check that raise an orm.except_orm
        3) Allow 2 Others with the other co_residency:
            * Check the 2 are now duplicate allowed
            * Check the 2 are no more duplicate detected
            * Check the 2 are associated with the co-residency
        4) Undo Allowed action by simulation of a push on ````
        """
        postal_XIDS = [
           'ficep_address.postal_coordinate_2',
           'ficep_address.postal_coordinate_2_duplicate_1',
           'ficep_address.postal_coordinate_2_duplicate_2',
           'ficep_address.postal_coordinate_2_duplicate_3'
        ]
        co_residency_XIDS = [
            'ficep_address.co_residency_id_1',
            'ficep_address.co_residency_id_2',
        ]
        postal_coordinates_ids = []
        co_residencies_id = []

        for xid in postal_XIDS:
            postal_coordinates_ids.append(self.ref(xid))
        for xid in co_residency_XIDS:
            co_residencies_id.append(self.ref(xid))
        ctx = {'active_model': self.postal_model,
               'active_ids': [postal_coordinates_ids[0], postal_coordinates_ids[1]]}
        wz_id = self.allow_duplicate_wizard_model.create(self.cr, self.uid,
                                                         {'co_residency_id': co_residencies_id[0]},
                                                         context=ctx)
        # Step One
        self.allow_duplicate_wizard_model.button_allow_duplicate(self.cr, self.uid, [wz_id], context=ctx)
        postal_coordinates = self.registry(self.postal_model).browse(self.cr, self.uid, [postal_coordinates_ids[0], postal_coordinates_ids[1]])
        #check allowed
        self.assertTrue(postal_coordinates[0].is_duplicate_allowed, 'Postal Coordinate 1 Must Be Allowed')
        self.assertTrue(postal_coordinates[0].is_duplicate_allowed, 'Postal Coordinate 2 Must Be Allowed')
        #check no more detected
        self.assertFalse(postal_coordinates[0].is_duplicate_detected, 'Postal Coordinate 1 Should not Be Duplicate Detected')
        self.assertFalse(postal_coordinates[1].is_duplicate_detected, 'Postal Coordinate 2 Should not Be Duplicate Detected')
        #check co residency
        self.assertEqual(postal_coordinates[0].co_residency_id.id, co_residencies_id[0], 'Postal Coordinate 1 Should not Be Duplicate Detected')
        self.assertEqual(postal_coordinates[1].co_residency_id.id, co_residencies_id[0], 'Postal Coordinate 2 Should not Be Duplicate Detected')
        # Step Two
        ctx = {'active_model': self.postal_model,
               'active_ids': [postal_coordinates_ids[2]]}
        wz_id = self.allow_duplicate_wizard_model.create(self.cr, self.uid,
                                                         {'co_residency_id': co_residencies_id[1]},
                                                         context=ctx)
        self.assertRaises(orm.except_orm, self.allow_duplicate_wizard_model.button_allow_duplicate, self.cr, self.uid, [wz_id], context=ctx)
        # Step Three
        ctx = {'active_model': self.postal_model,
               'active_ids': [postal_coordinates_ids[2], postal_coordinates_ids[3]]}
        wz_id = self.allow_duplicate_wizard_model.create(self.cr, self.uid,
                                                         {'co_residency_id': co_residencies_id[1]},
                                                         context=ctx)
        self.allow_duplicate_wizard_model.button_allow_duplicate(self.cr, self.uid, [wz_id], context=ctx)
        #check allowed
        postal_coordinates = self.registry(self.postal_model).browse(self.cr, self.uid, [postal_coordinates_ids[2], postal_coordinates_ids[3]])
        self.assertTrue(postal_coordinates[0].is_duplicate_allowed, 'Postal Coordinate 3 Must Be Allowed')
        self.assertTrue(postal_coordinates[1].is_duplicate_allowed, 'Postal Coordinate 4 Must Be Allowed')
        #check no more detected
        self.assertFalse(postal_coordinates[0].is_duplicate_detected, 'Postal Coordinate 3 Should not Be Duplicate Detected')
        self.assertFalse(postal_coordinates[1].is_duplicate_detected, 'Postal Coordinate 4 Should not Be Duplicate Detected')
        #check co residency
        self.assertEqual(postal_coordinates[0].co_residency_id.id, co_residencies_id[1], 'Postal Coordinate 3 Should Have Co-Residency 2')
        self.assertEqual(postal_coordinates[1].co_residency_id.id, co_residencies_id[1], 'Postal Coordinate 4 Should Have Co-Residency 2')
        #Step 4
        self.registry(self.postal_model).button_undo_allow_duplicate(self.cr, self.uid, postal_coordinates_ids)

        postal_coordinates = self.registry(self.postal_model).browse(self.cr, self.uid, postal_coordinates_ids)
        self.assertFalse(postal_coordinates[0].is_duplicate_allowed, 'Postal Coordinate 1 Must Not Be Allowed')
        self.assertFalse(postal_coordinates[1].is_duplicate_allowed, 'Postal Coordinate 2 Must Not Be Allowed')
        self.assertFalse(postal_coordinates[2].is_duplicate_allowed, 'Postal Coordinate 3 Must Not Be Allowed')
        self.assertFalse(postal_coordinates[3].is_duplicate_allowed, 'Postal Coordinate 4 Must Not Be Allowed')
        #check no more detected
        self.assertTrue(postal_coordinates[0].is_duplicate_detected, 'Postal Coordinate 3 Should Be Duplicate Detected')
        self.assertTrue(postal_coordinates[1].is_duplicate_detected, 'Postal Coordinate 4 Should Be Duplicate Detected')
        self.assertTrue(postal_coordinates[2].is_duplicate_detected, 'Postal Coordinate 3 Should Be Duplicate Detected')
        self.assertTrue(postal_coordinates[3].is_duplicate_detected, 'Postal Coordinate 4 Should Be Duplicate Detected')
        #check co residency
        self.assertFalse(postal_coordinates[0].co_residency_id.id, 'Postal Coordinate 3 Should not Have Co-Residency')
        self.assertFalse(postal_coordinates[1].co_residency_id.id, 'Postal Coordinate 4 Should not Have Co-Residency')
        self.assertFalse(postal_coordinates[2].co_residency_id.id, 'Postal Coordinate 3 Should not Have Co-Residency')
        self.assertFalse(postal_coordinates[3].co_residency_id.id, 'Postal Coordinate 4 Should not Have Co-Residency')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
