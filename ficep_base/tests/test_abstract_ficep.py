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


class abstract_ficep(object):

    def setUp(self):
        super(abstract_ficep, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.model_abstract = None
        self.invalidate_success_ids = None
        self.invalidate_fail_ids = None
        self.validate_ids = None

    def test_action_invalidate_success(self):
        res = self.model_abstract.action_invalidate(self.cr, self.uid, self.invalidate_success_ids, context=None)
        self.assertEqual(res, True)

        for obj in self.model_abstract.browse(self.cr, self.uid, self.invalidate_success_ids):
            self.assertEqual(obj.active, False)
            self.assertNotEqual(obj.expire_date, False)

    def test_action_invalidate_fail(self):
        self.assertRaises(orm.except_orm, self.model_abstract.action_invalidate, self.cr, self.uid, self.invalidate_fail_ids)

    def test_action_validate_success(self):
        res = self.model_abstract.action_validate(self.cr, self.uid, self.validate_ids, context=None)
        self.assertEqual(res, True)

        for obj in self.model_abstract.browse(self.cr, self.uid, self.validate_ids):
            self.assertEqual(obj.active, True)
            self.assertEqual(obj.expire_date, False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
