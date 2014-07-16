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

import psycopg2
import logging
from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.osv import orm
from openerp.addons.ficep_base import testtool

_logger = logging.getLogger(__name__)


class test_postal_mail(SharedSetupTransactionCase):
    _data_files = (
        '../../ficep_communication/demo/communication_demo.xml',
        'data/postal_mail_data.xml',
    )

    _module_ns = 'ficep_communication'

    def setUp(self):
        super(test_postal_mail, self).setUp()
        self._postal_mail_pool = self.registry('postal.mail')
        self._postal_mail_log_pool = self.registry('postal.mail.log')
        self._distribution_pool = self.registry('distribution.list')

        self.test_postal_mail = self.ref('%s.postal_mail_1' % self._module_ns)
        self.virtual_distribution_list = self.ref('ficep_communication.distribution_list')

    def test_unique_postal_mail(self):
        '''
            Postal mail name must be unique
        '''
        self._postal_mail_pool.create(self.cr, self.uid, {'name': 'Postal Mail'})
        with testtool.disable_log_error(self.cr):
            self.assertRaises(psycopg2.IntegrityError, self._postal_mail_pool.create, self.cr, self.uid,
                              {'name': 'Postal Mail'})

    def test_postal_mail_log_generation(self):
        '''
            Postal mail logs should be generated when exporting a CSV and linking a postal mail.
        '''
        mass_function_obj = self.registry['distribution.list.mass.function']
        wiz_id = mass_function_obj.create(self.cr, self.uid, {
            'trg_model': 'postal.coordinate',
            'p_mass_function': 'csv',
            'postal_mail_id': self.test_postal_mail
        })
        mcontext = {
            'active_id': self.virtual_distribution_list
        }
        postal_mail_logs_before = self._postal_mail_log_pool.search_count(self.cr, self.uid, [])
        mass_function_obj.mass_function(self.cr, self.uid, [wiz_id], context=mcontext)
        postal_mail_logs_after = self._postal_mail_log_pool.search_count(self.cr, self.uid, [])
        self.assertTrue(postal_mail_logs_after - postal_mail_logs_before > 0)