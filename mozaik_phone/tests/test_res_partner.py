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
from openerp.osv import fields
import logging
_logger = logging.getLogger(__name__)


class test_phone_coordinate_wizard(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        'data/phone_data.xml',
    )

    _module_ns = 'mozaik_phone'

    def setUp(self):
        super(test_phone_coordinate_wizard, self).setUp()

        self.partner_model = self.registry('res.partner')
        self.phone_model = self.registry('phone.phone')
        self.phone_coordinate_model = self.registry('phone.coordinate')

        self.partner_pauline_id = self.ref(
            '%s.res_partner_pauline' %
            self._module_ns)
        self.partner_nouvelobs_id = self.ref(
            '%s.res_partner_nouvelobs' %
            self._module_ns)
        self.phone_id_2 = self.ref(
            '%s.fix_for_test_update_2' % self._module_ns)
        self.phone_coordinate_id_1 = self.ref(
            '%s.phone_coo_for_test_update_1' %
            self._module_ns)

        self.context = {}

    def test_create_phone_coordinate(self):
        """
        ============================
        test_create_phone_coordinate
        ============================
        Test the fact that when a phone_coordinate is create for a partner,
        The phone value is right set
        """
        cr, uid, context = self.cr, self.uid, self.context
        partner_model = self.partner_model
        phone_coordinate_model = self.phone_coordinate_model
        partner_value = partner_model.read(
            cr,
            uid,
            self.partner_pauline_id,
            ['phone'],
            context=context)
        phone_value = phone_coordinate_model.browse(
            cr,
            uid,
            self.phone_coordinate_id_1,
            context=context).phone_id.name
        self.assertEqual(
            partner_value['phone'] == phone_value,
            True,
            "Phone Should Be Set With The Same Value")

    def test_update_phone_coordinate(self):
        """
        ============================
        test_update_phone_coordinate
        ============================
        Test the fact that when a phone_id is updated for a phone_coordinate
        The phone value is right set for the partner of this phone_coordinate
        """
        cr, uid, context = self.cr, self.uid, self.context
        partner_model = self.partner_model
        phone_coordinate_model = self.phone_coordinate_model

        phone_coordinate_model.write(
            cr, uid, [
                self.phone_coordinate_id_1], {
                'phone_id': self.phone_id_2}, context=context)
        partner_value = partner_model.read(
            cr,
            uid,
            self.partner_pauline_id,
            ['phone'],
            context=context)
        phone_value = phone_coordinate_model.browse(
            cr,
            uid,
            self.phone_coordinate_id_1,
            context=context).phone_id.name
        self.assertEqual(
            partner_value['phone'] == phone_value,
            True,
            "Phone Should Be Set With The Same Value")

    def test_update_phone_number(self):
        """
        ========================
        test_update_phone_number
        ========================
        Test the replication of the phone number of the main coordinate on
        the partner
        """
        cr, uid, context = self.cr, self.uid, self.context

        partner_model = self.partner_model
        phone_coordinate_model = self.phone_coordinate_model
        phone_model = self.phone_model

        phone_coordinate_model.write(
            cr, uid, [
                self.phone_coordinate_id_1], {
                'phone_id': self.phone_id_2}, context=context)
        phone_model.write(
            cr, uid, self.phone_id_2, {
                'name': '091452325'}, context=context)
        partner_value = partner_model.read(
            cr,
            uid,
            self.partner_pauline_id,
            ['phone'],
            context=context)
        phone_value = phone_coordinate_model.browse(
            cr,
            uid,
            self.phone_coordinate_id_1,
            context=context).phone_id.name
        self.assertEqual(
            partner_value['phone'] == phone_value,
            True,
            "Phone Should Be Set With The Same Value")

        phone_model.write(
            cr, uid, [
                self.phone_id_2], {
                'also_for_fax': True}, context=context)
        partner_value = partner_model.read(
            cr,
            uid,
            self.partner_pauline_id,
            ['fax'],
            context=context)
        self.assertEqual(
            partner_value['fax'] == phone_value,
            True,
            "Phone and Fax must be identical")

    def test_invalidate_partner(self):
        """
        =======================
        test_invalidate_partner
        =======================
        When invalidating a partner all its coordinates have to be invalidated
        """
        cr, uid, context = self.cr, self.uid, self.context
        nouvelobs_id = self.partner_nouvelobs_id
        partner_model = self.partner_model
        phone_coordinate_model = self.phone_coordinate_model
        phone_model = self.phone_model

        # Check for reference data
        nouvelobs = partner_model.browse(
            cr, uid, nouvelobs_id, context=context)
        nb_active_phone_coord = len(nouvelobs.phone_coordinate_ids)
        self.assertEqual(
            nb_active_phone_coord,
            1,
            'Wrong expected reference data for this test')
        self.assertEqual(
            nouvelobs.phone_coordinate_ids[0].coordinate_type,
            'fax',
            'Wrong expected reference data for this test')
        nb_inactive_phone_coord = len(nouvelobs.phone_coordinate_inactive_ids)
        self.assertEqual(
            nb_inactive_phone_coord,
            0,
            'Wrong expected reference data for this test')

        # Add a coordinate to the partner
        vals = {'name': '061785612', 'type': 'fix'}
        phone_id = phone_model.create(cr, uid, vals, context=context)
        coord_id = phone_coordinate_model.create(
            cr, uid, {
                'partner_id': nouvelobs_id, 'phone_id': phone_id, },
            context=context)
        self.assertTrue(coord_id, 'Create coordinate fails')
        nb_active_phone_coord += 1

        # Invalidate partner
        partner_model.write(cr,
                            uid,
                            [nouvelobs_id],
                            {'is_duplicate_detected': False,
                             'is_duplicate_allowed': False,
                             'active': False,
                             'expire_date': fields.datetime.now(),
                             },
                            context=context)

        # Check its phone coordinates
        nouvelobs = partner_model.browse(
            cr, uid, nouvelobs_id, context=context)
        self.assertEqual(len(nouvelobs.phone_coordinate_ids),
                         0,
                         'Invalidate partner fails with active coordinates')
        self.assertEqual(
            len(nouvelobs.phone_coordinate_inactive_ids),
            nb_active_phone_coord,
            'Invalidate partner fails with too few inactive coordinates')
