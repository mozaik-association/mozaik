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


class test_ext_mandate(SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        '../../ficep_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'ficep_mandate'
    _candidature_pool = False
    _committee_pool = False
    _mandate_pool = False

    def setUp(self):
        super(test_ext_mandate, self).setUp()
        self._candidature_pool = self.registry('ext.candidature')
        self._committee_pool = self.registry('ext.selection.committee')
        self._mandate_pool = self.registry('ext.mandate')

    def test_copy_ext_selection_committee(self):
        '''
            Test copy selection committee and keep rejected candidatures
        '''
        selection_committee = self.browse_ref('%s.sc_membre_effectif_ag' % self._module_ns)

        rejected_id = selection_committee.candidature_ids[0]
        self._candidature_pool.signal_button_reject(self.cr, self.uid, [rejected_id.id])

        res = self._committee_pool.action_copy(self.cr, self.uid, [selection_committee.id])
        new_committee_id = res['res_id']
        self.assertNotEqual(new_committee_id, False)

        candidature_commitee_id = self._candidature_pool.read(self.cr, self.uid, rejected_id.id, ['selection_committee_id'])['selection_committee_id']
        self.assertEqual(new_committee_id, candidature_commitee_id[0])

    def test_duplicate_ext_candidature_in_same_category(self):
        '''
        Try to create twice a candidature in the same category for a partner
        '''
        jacques_partner_id = self.ref('%s.res_partner_jacques' % self._module_ns)
        membre_eff_cat_id = self.ref('%s.mc_membre_effectif_ag' % self._module_ns)
        selection_committee_id = self.ref('%s.sc_membre_effectif_ag' % self._module_ns)

        committee = self._committee_pool.browse(self.cr, self.uid, selection_committee_id)

        data = dict(mandate_category_id=membre_eff_cat_id,
            selection_committee_id=selection_committee_id,
            designation_int_assembly_id=committee.designation_int_assembly_id.id,
            ext_assembly_id=committee.assembly_id.id,
            partner_id=jacques_partner_id)

        self._candidature_pool.create(self.cr, self.uid, data)

        with testtool.disable_log_error(self.cr):
            self.assertRaises(psycopg2.IntegrityError,
                              self._candidature_pool.create,
                              self.cr, self.uid, data)

    def test_ext_candidature_process(self):
        '''
        Test the process of internal candidatures until mandate creation
        '''
        committee_id = self.ref('%s.sc_membre_effectif_ag' % self._module_ns)
        ext_paul_id = self.ref('%s.ext_paul_membre_ag' % self._module_ns)
        ext_thierry_id = self.ref('%s.ext_thierry_membre_ag' % self._module_ns)
        candidature_ids = [ext_thierry_id, ext_paul_id]
        '''
           Attempt to accept candidatures before suggesting them
        '''
        self.assertRaises(orm.except_orm, self._committee_pool.button_accept_candidatures, self.cr, self.uid, [committee_id])

        '''
            Paul and Thierry are suggested
        '''
        self._candidature_pool.signal_button_suggest(self.cr, self.uid, candidature_ids)

        '''
            Candidatures are refused
        '''
        self._committee_pool.button_refuse_candidatures(self.cr, self.uid, [committee_id])
        for candidature_data in self._candidature_pool.read(self.cr, self.uid, candidature_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'declared')

        '''
            Paul candidature is rejected
        '''
        self._candidature_pool.signal_button_reject(self.cr, self.uid, [ext_paul_id])
        self.assertEqual(self._candidature_pool.read(self.cr, self.uid, ext_paul_id, ['state'])['state'], 'rejected')

        '''
            Thierry is suggested again
        '''
        candidature_ids = [ext_thierry_id]
        self._candidature_pool.signal_button_suggest(self.cr, self.uid, candidature_ids)

        for candidature_data in self._candidature_pool.read(self.cr, self.uid, candidature_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'suggested')

        '''
            Accept Candidatures
        '''
        self._committee_pool.write(self.cr, self.uid, [committee_id], {'decision_date': '2014-04-01'})
        self._committee_pool.button_accept_candidatures(self.cr, self.uid, [committee_id])
        for candidature_data in self._candidature_pool.read(self.cr, self.uid, candidature_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'elected')

        '''
            Mandate is automatically created for Thierry candidature
                                                - mandate is linked to candidature
        '''
        mandate_ids = self._mandate_pool.search(self.cr, self.uid, [('candidature_id', 'in', candidature_ids)])
        self.assertEqual(len(mandate_ids), 1)

    def test_no_decision_date(self):
        '''
        Test the process of accepting internal candidatures without decision date
        '''
        committee_id = self.ref('%s.sc_membre_effectif_ag' % self._module_ns)
        ext_paul_id = self.ref('%s.ext_paul_membre_ag' % self._module_ns)
        ext_thierry_id = self.ref('%s.ext_thierry_membre_ag' % self._module_ns)

        self._candidature_pool.signal_button_suggest(self.cr, self.uid, [ext_thierry_id])
        self._candidature_pool.signal_button_reject(self.cr, self.uid, [ext_paul_id])
        self.assertRaises(orm.except_orm, self._committee_pool.button_accept_candidatures, self.cr, self.uid, [committee_id])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
