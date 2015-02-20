# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from anybox.testing.openerp import SharedSetupTransactionCase


class test_postal_coordinate(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_base/tests/data/res_users_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        '../../mozaik_address/tests/data/reference_data.xml',
        '../../mozaik_address/tests/data/address_data.xml',
    )

    _module_ns = 'mozaik_membership'

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
        cr, uid = self.cr, self.uid
        pc_mod, wz_mod = self.postal_model,\
            self.allow_duplicate_wizard_model
        cr_mod = self.co_residency_model
        wiz_adr_mod = self.cores_change_adr_model
        new_adr_id = self.ref('%s.address_4' % self._module_ns)

        postal_XIDS = [
            'mozaik_membership.postal_coordinate_2',
            'mozaik_membership.postal_coordinate_2_duplicate_1',
            'mozaik_membership.postal_coordinate_2_duplicate_4',
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
        usr_marc = self.browse_ref('%s.res_users_marc' % self._module_ns)
        int_instance_id = self.ref('mozaik_structure.int_instance_01')

        partners = ['%s.res_partner_marc',
                    '%s.res_partner_jacques',
                    '%s.res_partner_paul']
        partner_ids = []
        for partner in partners:
            partner_ids.append(self.ref(partner % self._module_ns))
        vals = {
            'int_instance_id': int_instance_id,
            'int_instance_m2m_ids': [(6, 0, [int_instance_id])],
        }
        self.registry('res.partner').write(cr,
                                           uid,
                                           partner_ids,
                                           vals
                                           )

        use_allowed = wiz_adr_mod._use_allowed(cr,
                                               usr_marc.id,
                                               cor_id,
                                               context=ctx)
        self.assertFalse(use_allowed)
