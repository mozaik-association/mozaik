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
        self.assertRaises(orm.except_orm, model_email.create, cr, uid, {'partner_id': partner_id_1,
                                                                        'email': 'bad'})
        email_id = model_email.create(cr, uid, {'partner_id': partner_id_1,
                                                     'email': 'first bad AFTER right@ok.be'})
        self.assertEqual('firstbadafterright@ok.be',
                         model_email.browse(self.cr,
                                                 self.uid,
                                                 [email_id])[0].email,
                                                 'Email Should Not Contains Upper Case Or Whitespace')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
