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
import openerp.tests.common as common

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
        self.allow_duplicate_wizard_model = self.registry('allow.duplicate.address.wizard')
        self.postal_model = 'postal.coordinate'

    def test_all_duplicate_co_residency(self):
        """
        ===============================
        test_all_duplicate_co_residency
        ===============================
        Test requirement:
        4 duplicated postal coordinates
        Test Case:
        1) Allow 2 duplicates
            * Check the 2 are now allowed duplicates
            * Check the 2 are no more detected duplicates
            * Check associated co-residency associated to the coordinates
        2) Allow other duplicates
            * Check they are associated to the same co-residency
        3) Undo Allow Duplicates
            * All Coordinates must become detected duplicates without co-residency id
        """
        postal_XIDS = [
           'ficep_address.postal_coordinate_2',
           'ficep_address.postal_coordinate_2_duplicate_1',
           'ficep_address.postal_coordinate_2_duplicate_2',
           'ficep_address.postal_coordinate_2_duplicate_3',
        ]

        postal_coordinates_ids = []
        for xid in postal_XIDS:
            postal_coordinates_ids.append(self.ref(xid))

        # Step One
        ctx = {
            'active_model': self.postal_model,
            'active_ids': [postal_coordinates_ids[0], postal_coordinates_ids[1]],
            'get_co_residency': True,
        }
        vals = self.allow_duplicate_wizard_model.default_get(self.cr, self.uid, [], context=ctx)
        wz_id = self.allow_duplicate_wizard_model.create(self.cr, self.uid, vals, context=ctx)
        cor_id = self.allow_duplicate_wizard_model.button_allow_duplicate(self.cr, self.uid, [wz_id], context=ctx)
        postal_coordinates = self.registry(self.postal_model).browse(self.cr, self.uid, ctx['active_ids'])
        #check allowed
        self.assertTrue(postal_coordinates[0].is_duplicate_allowed, 'Postal Coordinate 1 Must Be Allowed')
        self.assertTrue(postal_coordinates[1].is_duplicate_allowed, 'Postal Coordinate 2 Must Be Allowed')
        #check no more detected
        self.assertFalse(postal_coordinates[0].is_duplicate_detected, 'Postal Coordinate 1 Should not Be Duplicate Detected')
        self.assertFalse(postal_coordinates[1].is_duplicate_detected, 'Postal Coordinate 2 Should not Be Duplicate Detected')
        #check co residency
        self.assertEqual(postal_coordinates[0].co_residency_id.id, cor_id, 'Wrong Co-Residency associated to Postal Coordinate 1')
        self.assertEqual(postal_coordinates[1].co_residency_id.id, cor_id, 'Wrong Co-Residency associated to Postal Coordinate 2')

        # Step Two
        ctx = {
            'active_model': self.postal_model,
            'active_ids': [postal_coordinates_ids[2], postal_coordinates_ids[3]],
            'get_co_residency': True,
        }
        vals = self.allow_duplicate_wizard_model.default_get(self.cr, self.uid, [], context=ctx)
        wz_id = self.allow_duplicate_wizard_model.create(self.cr, self.uid, vals, context=ctx)
        cor2_id = self.allow_duplicate_wizard_model.button_allow_duplicate(self.cr, self.uid, [wz_id], context=ctx)
        postal_coordinates = self.registry(self.postal_model).browse(self.cr, self.uid, ctx['active_ids'])
        #check co residency
        self.assertEqual(postal_coordinates[0].co_residency_id.id, cor2_id, 'Wrong Co-Residency associated to Postal Coordinate 3')
        self.assertEqual(postal_coordinates[1].co_residency_id.id, cor2_id, 'Wrong Co-Residency associated to Postal Coordinate 4')
        self.assertEqual(cor_id, cor2_id, 'Wrong Co-Residency associated to Postal Coordinates: [1,2] != [3,4]')

        #Step Three
        self.registry(self.postal_model).button_undo_allow_duplicate(self.cr, self.uid, [postal_coordinates_ids[2]])
        postal_coordinates = self.registry(self.postal_model).browse(self.cr, self.uid, postal_coordinates_ids)
        for i in range(4):
            self.assertFalse(postal_coordinates[i].is_duplicate_allowed, 'Postal Coordinate %s Must Be Not Allowed Duplicate' % i)
            self.assertTrue(postal_coordinates[i].is_duplicate_detected, 'Postal Coordinate %s Must Be Detected Duplicate' % i)
            self.assertFalse(postal_coordinates[i].co_residency_id.id, 'No co-residency Must Be associated to Postal Coordinate %s' % i)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
