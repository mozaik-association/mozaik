# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.osv import orm

import logging
_logger = logging.getLogger(__name__)


class test_create_user_from_partner(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_base/tests/data/res_users_data.xml',
        'data/res_partner_data.xml',
    )

    _module_ns = 'mozaik_person'

    def setUp(self):
        super(test_create_user_from_partner, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.partner_model = self.registry('res.partner')
        self.user_model = self.registry('res.users')
        self.p2u_wizard_model = self.registry('create.user.from.partner')

        self.partner_jacques_id = self.ref(
            '%s.res_partner_jacques' %
            self._module_ns)
        self.partner_paul_id = self.ref(
            '%s.res_partner_paul' % self._module_ns)

        self.group_fr_id = self.ref('mozaik_base.mozaik_res_groups_reader')

        _, self.portal_id = self.registry(
            'ir.model.data').get_object_reference(
            self.cr, self.uid, 'base', 'group_portal')

        self.context = {}

    def test_create_user_from_partner(self):
        """
        =============================
        test_create_user_from_partner
        =============================
        Test the creation of a user from a partner
        """
        cr, uid, context = self.cr, self.uid, self.context
        jacques_id, paul_id = self.partner_jacques_id, self.partner_paul_id
        fr_id = self.group_fr_id
        partner_model, user_model = self.partner_model, self.user_model

        # Check for reference data
        vals = user_model.search(
            cr, uid, [
                ('partner_id', '=', jacques_id)], context=context)
        self.assertFalse(
            len(vals),
            'Wrong expected reference data for this test')
        vals = partner_model.search(
            cr, uid, [
                ('id', '=', jacques_id), ('ldap_name', '>', '')],
            context=context)
        self.assertFalse(
            len(vals),
            'Wrong expected reference data for this test')
        vals = user_model.search(
            cr, uid, [
                ('partner_id', '=', paul_id)], context=context)
        self.assertTrue(
            len(vals),
            'Wrong expected reference data for this test')

        # Create a user from a partner
        user_id = partner_model.create_user(
            cr,
            uid,
            'jack',
            jacques_id,
            [fr_id],
            context=context)
        user = user_model.browse(cr, uid, user_id, context=context)
        self.assertEqual(
            user.partner_id.id,
            jacques_id,
            'Create user fails with wrong partner_id')
        self.assertEqual(
            user.login,
            'jack',
            'Create user fails with wrong login')
        self.assertTrue(
            fr_id in [
                g.id for g in user.groups_id],
            'Create user fails with wrong group')
        self.assertEqual(
            user.partner_id.ldap_name,
            'jack',
            'Update partner fails with wrong ldap_name')

        # Recreate a user from a partner
        self.assertRaises(
            orm.except_orm,
            self.partner_model.create_user,
            cr,
            uid,
            'popol',
            paul_id,
            [fr_id],
            context=context)

    def test_create_portal_user_from_partner(self):
        """
        ====================================
        test_create_portal_user_from_partner
        ====================================
        Test the creation of a portal user from a partner
        """
        cr, uid, context = self.cr, self.uid, self.context
        jacques_id = self.partner_jacques_id
        user_model = self.user_model
        p2u_wizard_model = self.p2u_wizard_model
        portal_id = self.portal_id

        # create a wizard record
        ctx = {
            'active_id': jacques_id,
        }
        vals = {
            'portal_only': True,
        }
        wz_id = p2u_wizard_model.create(cr, uid, vals, context=ctx)

        # Create a portal user from a partner
        user_id = p2u_wizard_model.create_user_from_partner(
            cr,
            uid,
            [wz_id],
            context=ctx)
        user = user_model.browse(cr, uid, user_id, context=context)
        grp_ids = [g.id for g in user.groups_id]
        self.assertEqual(
            user.partner_id.id,
            jacques_id,
            'Create user fails with wrong partner_id')
        self.assertEqual(
            user.login,
            user.partner_id.email,
            'Create user fails with wrong email')
        self.assertTrue(
            portal_id in grp_ids,
            'Create user fails with wrong group')
        self.assertEqual(len(grp_ids), 1,
                         'Create user fails with wrong groups')
