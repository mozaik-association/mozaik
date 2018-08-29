# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


def allow_duplicate(wz):
    action = wz.button_allow_duplicate()
    cor_id = action['res_id']
    return wz.env['co.residency'].browse(cor_id)


class TestPostalCoordinate(TransactionCase):

    def setUp(self):
        super().setUp()

        self.allow_duplicate_wizard_model = self.env[
            'allow.duplicate.address.wizard']
        self.postal_model = self.env['postal.coordinate']
        self.co_residency_model = self.env['co.residency']
        self.cores_change_adr_model = self.env['change.co.residency.address']

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
        pc_mod, wz_mod = self.postal_model, self.allow_duplicate_wizard_model
        postal_XIDS = [
            'mozaik_address.postal_coordinate_2',
            'mozaik_address.postal_coordinate_2_duplicate_1',
            'mozaik_address.postal_coordinate_2_duplicate_2',
            'mozaik_address.postal_coordinate_2_duplicate_3',
        ]

        all_pcs = pc_mod.browse()
        for xid in postal_XIDS:
            all_pcs += self.env.ref(xid)

        # Step One
        postal_coordinates = all_pcs[0] + all_pcs[1]
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': postal_coordinates.ids,
        }
        wz_mod_ctx = wz_mod.with_context(ctx)
        vals = wz_mod_ctx.default_get([])
        wz_id = wz_mod_ctx.create(vals)
        cor_id = allow_duplicate(wz_id)
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
            postal_coordinates[0].co_residency_id, cor_id,
            'Wrong Co-Residency associated to Postal Coordinate 1')
        self.assertEqual(
            postal_coordinates[1].co_residency_id, cor_id,
            'Wrong Co-Residency associated to Postal Coordinate 2')

        # Step Two
        postal_coordinates = all_pcs[2] + all_pcs[3]
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': postal_coordinates.ids,
        }
        wz_mod_ctx = wz_mod.with_context(ctx)
        vals = wz_mod_ctx.default_get([])
        wz_id = wz_mod_ctx.create(vals)
        cor2_id = allow_duplicate(wz_id)
        # check co residency
        self.assertEqual(
            postal_coordinates[0].co_residency_id, cor2_id,
            'Wrong Co-Residency associated to Postal Coordinate 3')
        self.assertEqual(
            postal_coordinates[1].co_residency_id, cor2_id,
            'Wrong Co-Residency associated to Postal Coordinate 4')
        self.assertEqual(
            cor_id, cor2_id,
            'Wrong Co-Residency associated to '
            'Postal Coordinates: [1,2] != [3,4]')

        # Step Three
        all_pcs[2].button_undo_allow_duplicate()
        for i in range(4):
            self.assertFalse(
                all_pcs[i].is_duplicate_allowed,
                'Postal Coordinate %s Must Be Not Allowed Duplicate' % i)
            self.assertTrue(
                all_pcs[i].is_duplicate_detected,
                'Postal Coordinate %s Must Be Detected Duplicate' % i)
            self.assertFalse(
                all_pcs[i].co_residency_id.id,
                'No co-all_pcs Must Be associated '
                'to Postal Coordinate %s' % i)

        # Step Four
        postal_coordinates = all_pcs[0] + all_pcs[1]
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': postal_coordinates.ids,
        }
        wz_mod_ctx = wz_mod.with_context(ctx)
        vals = wz_mod_ctx.default_get([])
        wz_id = wz_mod_ctx.create(vals)
        cor_id = allow_duplicate(wz_id)

        # Step Five
        cor_id.unlink()
        for i in range(2):
            self.assertFalse(
                postal_coordinates[i].is_duplicate_allowed,
                'Postal Coordinate %s Must Be Not Allowed Duplicate' % i)
            self.assertTrue(
                postal_coordinates[i].is_duplicate_detected,
                'Postal Coordinate %s Must Be Detected Duplicate' % i)
            self.assertFalse(
                postal_coordinates[i].co_residency_id,
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
        pc_mod, wz_mod = self.postal_model,\
            self.allow_duplicate_wizard_model
        cr_mod = self.co_residency_model
        wiz_adr_mod = self.cores_change_adr_model
        new_adr = self.env.ref('mozaik_address.address_4')

        postal_XIDS = [
            'mozaik_address.postal_coordinate_2',
            'mozaik_address.postal_coordinate_2_duplicate_1',
            'mozaik_address.postal_coordinate_2_duplicate_2',
        ]

        cor_ids = cr_mod.search([('address_id', '=', new_adr.id)])
        self.assertFalse(cor_ids)
        pc_ids = pc_mod.search([('address_id', '=', new_adr.id)])
        self.assertFalse(pc_ids)

        postal_coordinates = pc_mod.browse()
        for xid in postal_XIDS:
            postal_coordinates += self.env.ref(xid)

        # Step One
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': postal_coordinates.ids,
        }
        wz_mod_ctx = wz_mod.with_context(ctx)
        vals = wz_mod_ctx.default_get([])
        wz_id = wz_mod_ctx.create(vals)
        cor_id = allow_duplicate(wz_id)

        ctx = {
            'active_model': cr_mod._name,
            'active_ids': cor_id.ids,
        }
        wiz_adr_mod_ctx = wiz_adr_mod.with_context(ctx)
        wz_id = wiz_adr_mod_ctx.create({'address_id': new_adr.id,
                                        'invalidate': False})
        wz_id.change_address()

        cor_ids = cr_mod.search([('address_id', '=', new_adr.id)])
        self.assertNotEqual(cor_ids, False)
        self.assertNotEqual(cor_ids, cor_id)
        pc_ids = pc_mod.search([('address_id', '=', new_adr.id)])
        self.assertNotEqual(pc_ids, False)
        self.assertNotEqual(pc_ids, postal_coordinates)

        old_main = postal_coordinates[2]
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
        pc_mod, wz_mod = self.postal_model,\
            self.allow_duplicate_wizard_model
        cr_mod = self.co_residency_model
        wiz_adr_mod = self.cores_change_adr_model
        new_adr = self.env.ref('mozaik_address.address_4')

        postal_XIDS = [
            'mozaik_address.postal_coordinate_2',
            'mozaik_address.postal_coordinate_2_duplicate_1',
            'mozaik_address.postal_coordinate_2_duplicate_2',
        ]

        cor_ids = cr_mod.search([('address_id', '=', new_adr.id)])
        self.assertFalse(cor_ids)
        pc_ids = pc_mod.search([('address_id', '=', new_adr.id)])
        self.assertFalse(pc_ids)

        postal_coordinates = pc_mod.browse()
        for xid in postal_XIDS:
            postal_coordinates += self.env.ref(xid)

        # Step One
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': postal_coordinates.ids,
        }
        wz_mod_ctx = wz_mod.with_context(ctx)
        vals = wz_mod_ctx.default_get([])
        wz_id = wz_mod_ctx.create(vals)
        cor_id = allow_duplicate(wz_id)

        ctx = {
            'active_model': cr_mod._name,
            'active_ids': cor_id.ids,
        }
        wiz_adr_mod_ctx = wiz_adr_mod.with_context(ctx)
        wz_id = wiz_adr_mod_ctx .create({'address_id': new_adr.id,
                                         'invalidate': True})
        wz_id.change_address()

        cor_ids = cr_mod.search([('address_id', '=', new_adr.id)])
        self.assertNotEqual(cor_ids, False)
        self.assertNotEqual(cor_ids, cor_id)
        pc_ids = pc_mod.search([('address_id', '=', new_adr.id)])
        self.assertNotEqual(pc_ids, False)
        self.assertNotEqual(pc_ids, postal_coordinates)

        # check inactive
        self.assertFalse(cor_id.active)
        self.assertFalse(len(cor_id.postal_coordinate_ids))

        for coord in cor_id.postal_coordinate_ids:
            self.assertFalse(coord.active)
