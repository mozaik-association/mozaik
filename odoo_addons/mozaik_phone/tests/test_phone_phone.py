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
from openerp.osv import orm
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_phone_phone(common.TransactionCase):

    def setUp(self):
        super(test_phone_phone, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.model_phone = self.registry('phone.phone')

    def test_insert_without_prefix(self):
        """
        ==========================
        test_insert_without_prefix
        ==========================
        Test case:
        insert a valid phone number without prefix
        :insert: 061140220
        :expected: +32 61 14 02 20
        """
        cr, uid = self.cr, self.uid
        num = self.model_phone._check_and_format_number(cr, uid, '061140220')
        self.assertEquals(
            num,
            '+32 61 14 02 20',
            '061140220 should give +32 61 14 02 20')

    def test_insert_with_prefix(self):
        """
        =======================
        test_insert_with_prefix
        =======================
        Test case:
        insert a valid phone number with prefix
        :insert: +32489587520
        :expected: +32 489 58 75 20
        """
        cr, uid = self.cr, self.uid
        num = self.model_phone._check_and_format_number(
            cr, uid, '+32489587520')
        self.assertEquals(
            num,
            '+32 489 58 75 20',
            '+32489587520 should give +32 489 58 75 20')

    def test_proper_escaping(self):
        """
        ====================
        test_proper_escaping
        ====================
        Test case:
        insert a valid phone number with other characters in more
        :insert: 061-54/10    45
        :expected: +32 61 54 10 45
        """
        cr, uid = self.cr, self.uid
        num = self.model_phone._check_and_format_number(
            cr,
            uid,
            '061-54/10    45')
        self.assertEquals(
            num,
            '+32 61 54 10 45',
            '061-54/10    45 should give +32 61 54 10 45')

    def test_insert_bad_query(self):
        """
        =====================
        test_insert_bad_query
        =====================
        Test case:
        insert a bad format for a phone e.g. a word
        :insert: badquery
        :expected: orm_exception
        """
        cr, uid = self.cr, self.uid
        self.assertRaises(
            orm.except_orm,
            self.model_phone._check_and_format_number,
            cr,
            uid,
            'badquery',
            context={})
