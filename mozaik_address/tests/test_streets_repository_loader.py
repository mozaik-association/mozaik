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
import base64
from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
SUPERUSER_ID = common.ADMIN_USER_ID


class test_streets_repository_loader(SharedSetupTransactionCase):

    def setUp(self):
        super(test_streets_repository_loader, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        self.streets_repository_loader_model = self.registry('streets.repository.loader')
        self.address_local_street_model = self.registry('address.local.street')

    def test_update_local_streets(self):
        """
        =========================
        test_update_local_streets
        =========================
        Test create/update/disable with loader
        """
        content_text = '\n'.join(["9999999961201227Clos de /l'Estaminet(Ham-s-Heure)#",
                                 "1234567861201227NEW%OLD#",
                                 "9999999961201227-*-#"])
        data_file = base64.b64encode(content_text)

        cr = self.cr
        wiz_id = self.streets_repository_loader_model.create(cr, SUPERUSER_ID, {'ref_streets': data_file})
        self.streets_repository_loader_model.update_local_streets(cr, SUPERUSER_ID, [wiz_id])
        street_value = self.address_local_street_model.search_read(cr, SUPERUSER_ID,
                                                                 [('local_zip', '=', '6120'), ('identifier', '=', '1227')],
                                                                 fields=['disabled', 'local_street'])
        self.assertTrue(street_value[0]['disabled'], 'Should be to disable')
        self.assertTrue(street_value[0]['local_street'] == 'NEW', 'Local Street Should be `NEW`')

    def test_bad_insert(self):
        """
        ===============
        test_bad_insert
        ===============
        bad line: first 16 characters must be digits
        """
        data_file = base64.b64encode("""9999m999961201227Clos de /l'Estaminet(Ham-s-Heure)#
        """)

        cr = self.cr
        wiz_id = self.streets_repository_loader_model.create(cr, SUPERUSER_ID, {'ref_streets': data_file})
        self.assertRaises(orm.except_orm,
                          self.streets_repository_loader_model.update_local_streets,
                          cr, SUPERUSER_ID, [wiz_id])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
