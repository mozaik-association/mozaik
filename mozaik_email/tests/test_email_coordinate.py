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
from openerp.osv import orm
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_email_coordinate(common.TransactionCase):

    def setUp(self):
        super(test_email_coordinate, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_bad_insert(self):
        """
        ===============
        test_bad_insert
        ===============
        """
        cr, uid = self.cr, self.uid
        model_email = self.registry('email.coordinate')
        model_partner = self.registry('res.partner')
        partner_id_1 = model_partner.create(cr, uid, {'name': 'test'})
        self.assertRaises(
            orm.except_orm,
            model_email.create,
            cr, uid, {'partner_id': partner_id_1,
                      'email': 'bad'})
        email_id = model_email.create(
            cr, uid, {'partner_id': partner_id_1,
                      'email': 'first bad AFTER right@ok.be'})
        self.assertEqual(
            'firstbadafterright@ok.be',
            model_email.browse(
                self.cr, self.uid, [email_id])[0].email,
            'Email Should Not Contains Upper Case Or Whitespace')
