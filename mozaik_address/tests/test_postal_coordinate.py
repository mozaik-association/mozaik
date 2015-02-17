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


class test_postal_coordinate(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_base/tests/data/res_users_data.xml',
        'data/reference_data.xml',
        'data/address_data.xml',
    )

    _module_ns = 'mozaik_address'

    def setUp(self):
        super(test_postal_coordinate, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        self.allow_duplicate_wizard_model = self.registry(
            'allow.duplicate.address.wizard')
        self.postal_model = self.registry('postal.coordinate')
        self.co_residency_model = self.registry('co.residency')
        self.cores_change_adr_model = self.registry(
            'change.co.residency.address')

    def test_all_duplicate_co_residency(self):
        """
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
            * All Coordinates must become detected duplicates
              without co-residency id
        4) redo 1)
        5) Delete co-residency
            * idem 3)
        """
        cr, uid = self.cr, self.uid
        pc_mod, wz_mod = self.postal_model, self.allow_duplicate_wizard_model
        cr_mod = self.co_residency_model
        postal_XIDS = [
            'mozaik_address.postal_coordinate_2',
            'mozaik_address.postal_coordinate_2_duplicate_1',
            'mozaik_address.postal_coordinate_2_duplicate_2',
            'mozaik_address.postal_coordinate_2_duplicate_3',
        ]

        postal_coordinates_ids = []
        for xid in postal_XIDS:
            postal_coordinates_ids.append(self.ref(xid))

        # Step One
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': [
                postal_coordinates_ids[0],
                postal_coordinates_ids[1]
            ],
            'get_co_residency': True,
        }
        vals = wz_mod.default_get(cr, uid, [], context=ctx)
        wz_id = wz_mod.create(cr, uid, vals, context=ctx)
        cor_id = wz_mod.button_allow_duplicate(cr, uid, [wz_id], context=ctx)
        postal_coordinates = pc_mod.browse(cr, uid, ctx['active_ids'])
        # check allowed
        self.assertTrue(
            postal_coordinates[0].is_duplicate_allowed,
            'Postal Coordinate 1 Must Be Allowed')
        self.assertTrue(
            postal_coordinates[1].is_duplicate_allowed,
            'Postal Coordinate 2 Must Be Allowed')
        # check no more detected
        self.assertFalse(
            postal_coordinates[0].is_duplicate_detected,
            'Postal Coordinate 1 Should not Be Duplicate Detected')
        self.assertFalse(
            postal_coordinates[1].is_duplicate_detected,
            'Postal Coordinate 2 Should not Be Duplicate Detected')
        # check co residency
        self.assertEqual(
            postal_coordinates[0].co_residency_id.id, cor_id,
            'Wrong Co-Residency associated to Postal Coordinate 1')
        self.assertEqual(
            postal_coordinates[1].co_residency_id.id, cor_id,
            'Wrong Co-Residency associated to Postal Coordinate 2')

        # Step Two
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': [
                postal_coordinates_ids[2],
                postal_coordinates_ids[3]
            ],
            'get_co_residency': True,
        }
        vals = wz_mod.default_get(cr, uid, [], context=ctx)
        wz_id = wz_mod.create(cr, uid, vals, context=ctx)
        cor2_id = wz_mod.button_allow_duplicate(cr, uid, [wz_id], context=ctx)
        postal_coordinates = pc_mod.browse(cr, uid, ctx['active_ids'])
        # check co residency
        self.assertEqual(
            postal_coordinates[0].co_residency_id.id, cor2_id,
            'Wrong Co-Residency associated to Postal Coordinate 3')
        self.assertEqual(
            postal_coordinates[1].co_residency_id.id, cor2_id,
            'Wrong Co-Residency associated to Postal Coordinate 4')
        self.assertEqual(
            cor_id, cor2_id,
            'Wrong Co-Residency associated to '
            'Postal Coordinates: [1,2] != [3,4]')

        # Step Three
        pc_mod.button_undo_allow_duplicate(
            cr, uid, [postal_coordinates_ids[2]])
        postal_coordinates = pc_mod.browse(cr, uid, postal_coordinates_ids)
        for i in range(4):
            self.assertFalse(
                postal_coordinates[i].is_duplicate_allowed,
                'Postal Coordinate %s Must Be Not Allowed Duplicate' % i)
            self.assertTrue(
                postal_coordinates[i].is_duplicate_detected,
                'Postal Coordinate %s Must Be Detected Duplicate' % i)
            self.assertFalse(
                postal_coordinates[i].co_residency_id.id,
                'No co-residency Must Be associated '
                'to Postal Coordinate %s' % i)

        # Step Four
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': [
                postal_coordinates_ids[0],
                postal_coordinates_ids[1]
            ],
            'get_co_residency': True,
        }
        vals = wz_mod.default_get(cr, uid, [], context=ctx)
        wz_id = wz_mod.create(cr, uid, vals, context=ctx)
        cor_id = wz_mod.button_allow_duplicate(cr, uid, [wz_id], context=ctx)

        # Step Five
        cr_mod.unlink(cr, uid, cor_id)
        coords = pc_mod.browse(cr, uid, ctx['active_ids'])
        for i in range(2):
            self.assertFalse(
                coords[i].is_duplicate_allowed,
                'Postal Coordinate %s Must Be Not Allowed Duplicate' % i)
            self.assertTrue(
                coords[i].is_duplicate_detected,
                'Postal Coordinate %s Must Be Detected Duplicate' % i)
            self.assertFalse(
                coords[i].co_residency_id.id,
                'No co-residency Must Be associated '
                'to Postal Coordinate %s' % i)

    def test_change_co_residency_address(self):
        """
        Test requirement:
        2 duplicated postal coordinates
        Test Case:
        1) Allow 2 duplicates
            * Check associated co-residency associated to the coordinates
        2) Create a new address
        3) Move co-residency to the new address
            - create new postal coordinates
            - create new co-residency
        """
        cr, uid = self.cr, self.uid
        pc_mod, wz_mod = self.postal_model,\
            self.allow_duplicate_wizard_model
        cr_mod = self.co_residency_model
        wiz_adr_mod = self.cores_change_adr_model
        new_adr_id = self.ref('mozaik_address.address_4')

        postal_XIDS = [
            'mozaik_address.postal_coordinate_2',
            'mozaik_address.postal_coordinate_2_duplicate_1',
            'mozaik_address.postal_coordinate_2_duplicate_2',
        ]

        cor_ids = cr_mod.search(cr, uid, [('address_id', '=', new_adr_id)])
        self.assertFalse(cor_ids)
        pc_ids = pc_mod.search(cr, uid, [('address_id', '=', new_adr_id)])
        self.assertFalse(pc_ids)

        postal_coordinates_ids = []
        for xid in postal_XIDS:
            postal_coordinates_ids.append(self.ref(xid))

        # Step One
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': postal_coordinates_ids,
            'get_co_residency': True,
        }
        vals = wz_mod.default_get(cr, uid, [], context=ctx)
        wz_id = wz_mod.create(cr, uid, vals, context=ctx)
        cor_id = wz_mod.button_allow_duplicate(cr, uid, [wz_id], context=ctx)

        ctx = {
            'active_model': cr_mod._name,
            'active_ids': [cor_id],
        }
        wz_id = wiz_adr_mod.create(cr,
                                   uid,
                                   {'address_id': new_adr_id,
                                    'invalidate': False},
                                   context=ctx)
        wiz_adr_mod.change_address(cr, uid, [wz_id], context=ctx)

        cor_ids = cr_mod.search(cr, uid, [('address_id', '=', new_adr_id)])
        self.assertNotEqual(cor_ids, False)
        self.assertNotEqual(cor_ids[0], cor_id)
        pc_ids = pc_mod.search(cr, uid, [('address_id', '=', new_adr_id)])
        self.assertNotEqual(pc_ids, False)
        pc_ids.sort()
        postal_coordinates_ids.sort()
        self.assertNotEqual(pc_ids, postal_coordinates_ids)

        old_main = pc_mod.browse(cr, uid, postal_coordinates_ids[2])
        self.assertFalse(old_main.is_main)

    def test_change_co_residency_address_invalidate(self):
        """
        Test requirement:
        2 duplicated postal coordinates
        Test Case:
        1) Allow 2 duplicates
            * Check associated co-residency associated to the coordinates
        2) Create a new address
        3) Move co-residency to the new address
            - create new postal coordinates
            - create new co-residency
            - invalidate old co-residency and postal coordinates
        """
        cr, uid = self.cr, self.uid
        pc_mod, wz_mod = self.postal_model,\
            self.allow_duplicate_wizard_model
        cr_mod = self.co_residency_model
        wiz_adr_mod = self.cores_change_adr_model
        new_adr_id = self.ref('mozaik_address.address_4')

        postal_XIDS = [
            'mozaik_address.postal_coordinate_2',
            'mozaik_address.postal_coordinate_2_duplicate_1',
            'mozaik_address.postal_coordinate_2_duplicate_2',
        ]

        cor_ids = cr_mod.search(cr, uid, [('address_id', '=', new_adr_id)])
        self.assertFalse(cor_ids)
        pc_ids = pc_mod.search(cr, uid, [('address_id', '=', new_adr_id)])
        self.assertFalse(pc_ids)

        postal_coordinates_ids = []
        for xid in postal_XIDS:
            postal_coordinates_ids.append(self.ref(xid))

        # Step One
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': postal_coordinates_ids,
            'get_co_residency': True,
        }
        vals = wz_mod.default_get(cr, uid, [], context=ctx)
        wz_id = wz_mod.create(cr, uid, vals, context=ctx)
        cor_id = wz_mod.button_allow_duplicate(cr, uid, [wz_id], context=ctx)

        ctx = {
            'active_model': cr_mod._name,
            'active_ids': [cor_id],
        }
        wz_id = wiz_adr_mod.create(cr,
                                   uid,
                                   {'address_id': new_adr_id,
                                    'invalidate': True},
                                   context=ctx)
        wiz_adr_mod.change_address(cr, uid, [wz_id], context=ctx)

        cor_ids = cr_mod.search(cr, uid, [('address_id', '=', new_adr_id)])
        self.assertNotEqual(cor_ids, False)
        self.assertNotEqual(cor_ids[0], cor_id)
        pc_ids = pc_mod.search(cr, uid, [('address_id', '=', new_adr_id)])
        self.assertNotEqual(pc_ids, False)
        pc_ids.sort()
        postal_coordinates_ids.sort()
        self.assertNotEqual(pc_ids, postal_coordinates_ids)

        # check inactive
        co_res = cr_mod.browse(cr, uid, cor_id)
        self.assertFalse(co_res.active)

        for coord in co_res.postal_coordinate_ids:
            self.assertFalse(coord.active)
