# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class test_abstract_model(object):

    def setUp(self):
        super(test_abstract_model, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.model_abstract = None
        self.invalidate_success_ids = None
        self.invalidate_fail_ids = None
        self.validate_ids = None

    def test_action_invalidate_success(self):
        res = self.model_abstract.action_invalidate(
            self.cr, self.uid, self.invalidate_success_ids, context=None)
        self.assertEqual(res, True)

        for obj in self.model_abstract.browse(
                self.cr, self.uid, self.invalidate_success_ids):
            self.assertEqual(obj.active, False)
            self.assertNotEqual(obj.expire_date, False)

    def test_action_invalidate_fail(self):
        self.assertRaises(
            orm.except_orm,
            self.model_abstract.action_invalidate,
            self.cr, self.uid, self.invalidate_fail_ids)

    def test_action_revalidate_success(self):
        res = self.model_abstract.action_revalidate(
            self.cr, self.uid, self.validate_ids, context=None)
        self.assertEqual(res, True)

        for obj in self.model_abstract.browse(
                self.cr, self.uid, self.validate_ids):
            self.assertEqual(obj.active, True)
            self.assertEqual(obj.expire_date, False)
