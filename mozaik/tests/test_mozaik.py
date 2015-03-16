# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_email, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_email is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_email is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_email.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from anybox.testing.openerp import SharedSetupTransactionCase


class test_mozaik(SharedSetupTransactionCase):

    _module_ns = 'mozaik'

    def setUp(self):
        super(test_mozaik, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_recompute(self):
        """
        This test cover refactored feature due to this Odoo modification:
        https://github.com/odoo/odoo/pull/4905#issuecomment-78961983
        by assuring that a lambda user can add a record into the one2many
        coordinates from a partner's form
        """
        user = self.env.ref('%s.demo_user_test' % self._module_ns)
        email_vals = {
            'partner_id': user.partner_id.id,
            'email': 'test@test.be',
        }
        vals = {
            'email_coordinate_ids': [[0, False, email_vals]],
        }

        user.partner_id.sudo(user).write(vals)
        self.assertTrue(
            len(user.partner_id.email_coordinate_ids) == 2,
            'Should have a two email coordinate')
