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

from openerp.addons.mozaik_base import testtool

_logger = logging.getLogger(__name__)


class test_int_mandate(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'mozaik_mandate'
    _candidature_pool = False
    _committee_pool = False
    _mandate_pool = False

    def setUp(self):
        super(test_int_mandate, self).setUp()
        self._candidature_pool = self.registry('int.candidature')
        self._committee_pool = self.registry('int.selection.committee')
        self._mandate_pool = self.registry('int.mandate')

    def test_copy_int_selection_committee(self):
        '''
            Test copy selection committee and keep rejected candidatures
        '''
        cr, uid, context = self.cr, self.uid, {}

        selection_committee = self.browse_ref('%s.sc_secretaire_regional' %
                                              self._module_ns)

        rejected_id = selection_committee.candidature_ids[0]
        self._candidature_pool.signal_workflow(cr,
                                               uid,
                                               [rejected_id.id],
                                               'button_reject',
                                               context=context)

        res = self._committee_pool.action_copy(cr,
                                               uid,
                                               [selection_committee.id])
        new_committee_id = res['res_id']
        self.assertNotEqual(new_committee_id, False)

        candidature_commitee_id =\
                self._candidature_pool.read(self.cr,
                                            self.uid,
                                            rejected_id.id,
                                            ['selection_committee_id']\
                                            )['selection_committee_id']
        self.assertEqual(new_committee_id, candidature_commitee_id[0])

    def test_duplicate_int_candidature_in_same_category(self):
        '''
        Try to create twice a candidature in the same category for a partner
        '''
        jacques_partner_id = self.ref('%s.res_partner_jacques' %
                                      self._module_ns)
        conseil_comm_cat_id = self.ref('%s.mc_secretaire_regional' %
                                       self._module_ns)
        selection_committee_id = self.ref('%s.sc_secretaire_regional' %
                                          self._module_ns)

        committee = self._committee_pool.browse(self.cr,
                                                self.uid,
                                                selection_committee_id)

        data = dict(mandate_category_id=conseil_comm_cat_id,
         selection_committee_id=selection_committee_id,
         designation_int_assembly_id=committee.designation_int_assembly_id.id,
         int_assembly_id=committee.assembly_id.id,
         partner_id=jacques_partner_id)

        self._candidature_pool.create(self.cr, self.uid, data)

        with testtool.disable_log_error(self.cr):
            self.assertRaises(psycopg2.IntegrityError,
                              self._candidature_pool.create,
                              self.cr, self.uid, data)

    def test_int_candidature_process(self):
        '''
        Test the process of internal candidatures until mandate creation
        '''
        cr, uid, context = self.cr, self.uid, {}

        committee_id = self.ref('%s.sc_secretaire_regional' % self._module_ns)
        int_paul_id = self.ref('%s.int_paul_secretaire' % self._module_ns)
        int_thierry_secretaire_id = self.ref('%s.int_thierry_secretaire' %
                                             self._module_ns)
        candidature_ids = [int_thierry_secretaire_id, int_paul_id]
        '''
           Attempt to accept candidatures before suggesting them
        '''
        self.assertRaises(orm.except_orm,
                          self._committee_pool.button_accept_candidatures,
                          self.cr,
                          self.uid,
                          [committee_id])

        '''
            Paul and Thierry are suggested
        '''
        self._candidature_pool.signal_workflow(cr,
                                               uid,
                                               candidature_ids,
                                               'button_suggest',
                                               context=context)

        '''
            Candidatures are refused
        '''
        self._committee_pool.button_refuse_candidatures(self.cr,
                                                        self.uid,
                                                        [committee_id])
        for candidature_data in self._candidature_pool.read(self.cr,
                                                            self.uid,
                                                            candidature_ids,
                                                            ['state']):
            self.assertEqual(candidature_data['state'], 'declared')

        '''
            Paul candidature is rejected
        '''
        self._candidature_pool.signal_workflow(cr,
                                               uid,
                                               [int_paul_id],
                                               'button_reject',
                                               context=context)
        self.assertEqual(self._candidature_pool.read(self.cr,
                                                     self.uid,
                                                     int_paul_id,
                                                     ['state'])['state'],
                         'rejected')

        '''
            Thierry is suggested again
        '''
        candidature_ids = [int_thierry_secretaire_id]
        self._candidature_pool.signal_workflow(cr,
                                               uid,
                                               candidature_ids,
                                               'button_suggest',
                                               context=context)

        for candidature_data in self._candidature_pool.read(self.cr,
                                                            self.uid,
                                                            candidature_ids,
                                                            ['state']):
            self.assertEqual(candidature_data['state'], 'suggested')

        '''
            Accept Candidatures
        '''
        self._committee_pool.write(self.cr,
                                   self.uid,
                                   [committee_id],
                                   {'decision_date': '2014-04-01'})
        self._committee_pool.button_accept_candidatures(self.cr,
                                                        self.uid,
                                                        [committee_id])
        for candidature_data in self._candidature_pool.read(self.cr,
                                                            self.uid,
                                                            candidature_ids,
                                                            ['state']):
            self.assertEqual(candidature_data['state'], 'elected')

        '''
            Mandate is automatically created for Thierry candidature
                                        - mandate is linked to candidature
        '''
        mandate_ids = self._mandate_pool.search(self.cr,
                                                self.uid,
                                                [('candidature_id',
                                                  'in', candidature_ids)])
        self.assertEqual(len(mandate_ids), 1)

    def test_no_decision_date(self):
        '''
        Test the process of accepting internal candidatures without decision
        date
        '''
        cr, uid, context = self.cr, self.uid, {}

        committee_id = self.ref('%s.sc_secretaire_regional' % self._module_ns)
        int_paul_id = self.ref('%s.int_paul_secretaire' % self._module_ns)
        int_thierry_secretaire_id = self.ref('%s.int_thierry_secretaire' %
                                             self._module_ns)

        self._candidature_pool.signal_workflow(cr,
                                               uid,
                                               [int_thierry_secretaire_id],
                                               'button_suggest',
                                               context=context)
        self._candidature_pool.signal_workflow(cr,
                                               uid,
                                               [int_paul_id],
                                               'button_reject',
                                               context=context)
        self.assertRaises(orm.except_orm,
                          self._committee_pool.button_accept_candidatures,
                          self.cr,
                          self.uid,
                          [committee_id])
