# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from uuid import uuid4
import psycopg2
import logging
from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.addons.mozaik_base import testtool

_logger = logging.getLogger(__name__)


class test_postal_mail(SharedSetupTransactionCase):
    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_address/tests/data/reference_data.xml',
        '../../mozaik_address/tests/data/address_data.xml',
        'data/communication_data.xml',
        'data/postal_mail_data.xml',
    )

    _module_ns = 'mozaik_communication'

    def setUp(self):
        super(test_postal_mail, self).setUp()
        self._postal_mail_pool = self.registry('postal.mail')
        self._postal_mail_log_pool = self.registry('postal.mail.log')

        self.test_postal_mail = self.ref('%s.postal_mail_1' % self._module_ns)
        self.test_distribution_list = self.ref(
            '%s.distribution_list' % self._module_ns)

    def test_unique_postal_mail(self):
        '''
            Postal mail name must be unique
        '''
        self._postal_mail_pool.create(
            self.cr, self.uid, {'name': 'Postal Mail'})
        with testtool.disable_log_error(self.cr):
            self.assertRaises(
                psycopg2.IntegrityError,
                self._postal_mail_pool.create, self.cr, self.uid,
                {'name': 'Postal Mail'})

    def test_postal_mail_log_generation(self):
        '''
            Postal mail logs should be generated when exporting a CSV and
            linking a postal mail.
        '''
        mass_function_obj = self.registry['distribution.list.mass.function']
        wiz_id = mass_function_obj.create(self.cr, self.uid, {
            'trg_model': 'postal.coordinate',
            'p_mass_function': 'csv',
            'postal_mail_name': '%s' % uuid4(),
            'distribution_list_id': self.test_distribution_list,
        })
        postal_mail_logs_before = self._postal_mail_log_pool.search_count(
            self.cr, self.uid, [])
        mass_function_obj.mass_function(
            self.cr, self.uid, [wiz_id], context={})
        postal_mail_logs_after = self._postal_mail_log_pool.search_count(
            self.cr, self.uid, [])
        self.assertTrue(postal_mail_logs_after - postal_mail_logs_before > 0)
