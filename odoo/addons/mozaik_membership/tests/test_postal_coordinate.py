# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestPostalCoordinate(TransactionCase):

    def setUp(self):
        super().setUp()

        self.allow_duplicate_wizard_model = self.env[
            'allow.duplicate.address.wizard']
        self.postal_model = self.env['postal.coordinate']
        self.co_residency_model = self.env['co.residency']
        self.cores_change_adr_model = self.env[
            'change.co.residency.address']

    def test_change_co_residency_rights(self):
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
            'mozaik_address.postal_coordinate_2_duplicate_4',
        ]

        cor_ids = cr_mod.search([('address_id', '=', new_adr.id)])
        self.assertFalse(cor_ids)
        pc_ids = pc_mod.search([('address_id', '=', new_adr.id)])
        self.assertFalse(pc_ids)

        postal_coordinates = self.env["postal.coordinate"].browse()
        for xid in postal_XIDS:
            postal_coordinates += self.env.ref(xid)

        # Step One
        ctx = {
            'active_model': pc_mod._name,
            'active_ids': postal_coordinates.ids,
            'get_co_residency': True,
        }
        wz_mod_ctx = wz_mod.with_context(ctx)
        vals = wz_mod_ctx.default_get([])
        wz_id = wz_mod_ctx.create(vals)
        cor_id = wz_id.button_allow_duplicate()["res_id"]

        ctx = {
            'active_model': cr_mod._name,
            'active_ids': [cor_id],
        }
        usr_marc = self.env.ref('mozaik_membership.res_users_marc')
        int_instance_id = self.env.ref('mozaik_structure.int_instance_01')

        partners_xmlid = ['mozaik_coordinate.res_partner_marc',
                          'mozaik_coordinate.res_partner_jacques',
                          'mozaik_coordinate.res_partner_paul']
        partners = self.env["res.partner"].browse()
        for partner in partners_xmlid:
            partners += self.env.ref(partner)
        vals = {
            'int_instance_id': int_instance_id.id,
            'int_instance_m2m_ids': [(6, 0, [int_instance_id.id])],
        }
        partners.write(vals)

        use_allowed = wiz_adr_mod.with_context(ctx).sudo(user=usr_marc.id)\
            ._use_allowed(cor_id)
        self.assertFalse(use_allowed)
