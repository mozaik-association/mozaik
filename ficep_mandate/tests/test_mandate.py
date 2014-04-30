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

from openerp.addons.ficep_base import testtool

_logger = logging.getLogger(__name__)


class test_mandate(SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        '../../ficep_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'ficep_mandate'

    def setUp(self):
        super(test_mandate, self).setUp()

    def test_avoid_duplicate_mandate_category(self):
        '''
            Test unique name of mandate category
        '''
        int_power_level_01_id = self.ref('ficep_structure.int_power_level_01')
        int_power_level_02_id = self.ref('%s.int_power_level_02' % self._module_ns)

        data = dict(name='category_01', int_power_level_id=int_power_level_01_id)
        self.registry('mandate.category').create(self.cr, self.uid, data)
        data['int_power_level_id'] = int_power_level_02_id

        with testtool.disable_log_error(self.cr):
            self.assertRaises(psycopg2.IntegrityError,
                              self.registry('mandate.category').create,
                              self.cr, self.uid, data)

    def test_copy_selection_committee(self):
        '''
            Test copy selection committee and keep rejected candidatures
        '''
        candidature_pool = self.registry('sta.candidature')
        committee_pool = self.registry('selection.committee')
        selection_committee = self.browse_ref('%s.sc_tete_huy_communale' % self._module_ns)

        rejected_id = selection_committee.sta_candidature_ids[0]
        candidature_pool.signal_button_reject(self.cr, self.uid, [rejected_id.id])

        res = committee_pool.action_copy(self.cr, self.uid, [selection_committee.id])
        new_committee_id = res['res_id']
        self.assertNotEqual(new_committee_id, False)

        candidature_commitee_id = candidature_pool.read(self.cr, self.uid, rejected_id.id, ['selection_committee_id'])['selection_committee_id']
        self.assertEqual(new_committee_id, candidature_commitee_id[0])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
