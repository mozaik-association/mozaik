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


class test_sta_mandate(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'mozaik_mandate'

    def setUp(self):
        super(test_sta_mandate, self).setUp()

    def test_copy_sta_selection_committee(self):
        '''
            Test copy selection committee and keep rejected candidatures
        '''
        cr, uid, context = self.cr, self.uid, {}
        candidature_pool = self.registry('sta.candidature')
        committee_pool = self.registry('sta.selection.committee')
        selection_committee = self.browse_ref('%s.sc_tete_huy_communale' %
                                              self._module_ns)

        rejected_id = selection_committee.candidature_ids[0]
        candidature_pool.signal_workflow(cr,
                                         uid,
                                         [rejected_id.id],
                                         'button_reject',
                                         context=context)
        res = committee_pool.action_copy(cr, uid, [selection_committee.id])
        new_committee_id = res['res_id']
        self.assertNotEqual(new_committee_id, False)

        candidature_commitee_id = candidature_pool.read(
                                                    self.cr,
                                                    self.uid,
                                                    rejected_id.id,
                                                    ['selection_committee_id']
                                                    )['selection_committee_id']
        self.assertEqual(new_committee_id, candidature_commitee_id[0])

    def test_duplicate_sta_candidature_in_same_category(self):
        '''
        Try to create twice a candidature in the same category for a partner
        '''
        jacques_partner_id = self.ref('%s.res_partner_jacques' %
                                      self._module_ns)
        conseil_comm_cat_id = self.ref('%s.mc_conseiller_communal' %
                                       self._module_ns)
        selection_committee_id = self.ref('%s.sc_tete_huy_communale' %
                                          self._module_ns)

        committee =\
        self.registry('sta.selection.committee').browse(self.cr,
                                                        self.uid,
                                                        selection_committee_id)

        data = dict(mandate_category_id=conseil_comm_cat_id,
         selection_committee_id=selection_committee_id,
         designation_int_assembly_id=committee.designation_int_assembly_id.id,
         legislature_id=committee.legislature_id.id,
         electoral_district_id=committee.electoral_district_id.id,
         sta_assembly_id=committee.assembly_id.id,
         partner_id=jacques_partner_id)

        with testtool.disable_log_error(self.cr):
            self.assertRaises(psycopg2.IntegrityError,
                              self.registry('sta.candidature').create,
                              self.cr, self.uid, data)

    def test_sta_candidature_legislative_process(self):
        '''
        Test the process of states candidatures for a legislative assembly
        until mandate creation
        '''
        cr, uid, context = self.cr, self.uid, {}

        candidature_pool = self.registry('sta.candidature')
        mandate_pool = self.registry('sta.mandate')
        committee_pool = self.registry('sta.selection.committee')
        committee_id = self.ref('%s.sc_tete_huy_communale' % self._module_ns)
        sta_paul_communal_id = self.ref('%s.sta_paul_communal' %
                                        self._module_ns)
        sta_pauline_communal_id = self.ref('%s.sta_pauline_communal' %
                                           self._module_ns)
        sta_marc_communal_id = self.ref('%s.sta_marc_communal' %
                                        self._module_ns)
        sta_thierry_communal_id = self.ref('%s.sta_thierry_communal' %
                                           self._module_ns)
        sta_jacques_communal_id = self.ref('%s.sta_jacques_communal' %
                                           self._module_ns)
        candidature_ids = [sta_paul_communal_id,
                           sta_pauline_communal_id,
                           sta_marc_communal_id,
                           sta_thierry_communal_id,
                           sta_jacques_communal_id]
        '''
           Attempt to accept candidatures before suggesting them
        '''
        self.assertRaises(orm.except_orm,
                          committee_pool.button_accept_candidatures,
                          cr,
                          uid,
                          [committee_id])

        '''
            Paul, Pauline, Marc and Thierry candidatures are suggested
        '''
        candidature_pool.signal_workflow(cr,
                                         uid,
                                         candidature_ids,
                                         'button_suggest',
                                         context=context)

        for candidature_data in candidature_pool.read(self.cr,
                                                      self.uid,
                                                      candidature_ids,
                                                      ['state']):
            self.assertEqual(candidature_data['state'], 'suggested')

        '''
            Candidatures are refused
        '''
        committee_pool.button_refuse_candidatures(self.cr,
                                                  self.uid,
                                                  [committee_id])
        for candidature_data in candidature_pool.read(self.cr,
                                                      self.uid,
                                                      candidature_ids,
                                                      ['state']):
            self.assertEqual(candidature_data['state'], 'declared')

        '''
            Paul candidature is rejected
        '''
        candidature_pool.signal_workflow(cr,
                                         uid,
                                         [sta_paul_communal_id],
                                         'button_reject',
                                         context=context)
        self.assertEqual(candidature_pool.read(self.cr,
                                               self.uid,
                                               sta_paul_communal_id,
                                               ['state'])['state'], 'rejected')

        '''
            Pauline, Marc and Thierry candidatures are suggested again
        '''
        candidature_ids = [sta_pauline_communal_id,
                           sta_marc_communal_id,
                           sta_thierry_communal_id,
                           sta_jacques_communal_id]
        candidature_pool.signal_workflow(cr,
                                         uid,
                                         candidature_ids,
                                         'button_suggest',
                                         context=context)

        for candidature_data in candidature_pool.read(self.cr,
                                                      self.uid,
                                                      candidature_ids,
                                                      ['state']):
            self.assertEqual(candidature_data['state'], 'suggested')

        '''
            Accept Candidatures
        '''
        committee_pool.write(self.cr, self.uid, [committee_id],
                             {'decision_date': '2014-04-01'})
        committee_pool.button_accept_candidatures(self.cr,
                                                  self.uid,
                                                  [committee_id])
        for candidature_data in candidature_pool.read(self.cr,
                                                      self.uid,
                                                      candidature_ids,
                                                      ['state']):
            self.assertEqual(candidature_data['state'], 'designated')

        '''
            Result of election:
                            - Pauline is not elected
                            - Marc and Thierry are elected
        '''
        non_elected_ids = [sta_pauline_communal_id]
        elected_ids = [sta_marc_communal_id, sta_thierry_communal_id]

        candidature_pool.signal_workflow(cr,
                                         uid,
                                         non_elected_ids,
                                         'button_non_elected',
                                         context=context)
        for candidature_data in candidature_pool.read(cr,
                                                      uid,
                                                      non_elected_ids,
                                                      ['state']):
            self.assertEqual(candidature_data['state'], 'non-elected')

        candidature_pool.signal_workflow(cr,
                                         uid,
                                         elected_ids,
                                         'button_elected',
                                         context=context)
        for candidature_data in candidature_pool.read(cr,
                                                      uid,
                                                      elected_ids,
                                                      ['state']):
            self.assertEqual(candidature_data['state'], 'elected')

        '''
            Create Mandates for elected candidatures:
                                     - mandates are linked to candidatures
        '''
        candidature_pool.button_create_mandate(cr, uid, elected_ids)
        mandate_ids = mandate_pool.search(cr,
                                          uid,
                                          [('candidature_id',
                                            'in', elected_ids)])
        self.assertEqual(len(mandate_ids), len(elected_ids))

    def test_sta_candidature_not_legislative_process(self):
        '''
        Test the process of states candidatures for a non legislative assembly
        until mandate creation
        '''
        cr, uid, context = self.cr, self.uid, {}

        candidature_pool = self.registry('sta.candidature')
        mandate_pool = self.registry('sta.mandate')
        committee_pool = self.registry('sta.selection.committee')
        committee_id = self.ref('%s.sc_bourgmestre_huy' % self._module_ns)
        sta_marc_id = self.ref('%s.sta_marc_bourgmestre' % self._module_ns)
        candidature_pool.signal_workflow(cr,
                                         uid,
                                         [sta_marc_id],
                                         'button_suggest',
                                         context=context)

        candidature_data = candidature_pool.read(cr,
                                                 uid,
                                                 sta_marc_id,
                                                 ['state'])
        self.assertEqual(candidature_data['state'], 'suggested')

        committee_pool.write(cr, uid, [committee_id],
                             {'decision_date': '2014-04-01'})
        committee_pool.button_accept_candidatures(self.cr,
                                                  self.uid,
                                                  [committee_id])
        candidature_data = candidature_pool.read(self.cr,
                                                 self.uid,
                                                 sta_marc_id,
                                                 ['state'])
        self.assertEqual(candidature_data['state'], 'elected')

        mandate_ids = mandate_pool.search(self.cr,
                                          self.uid,
                                          [('candidature_id',
                                            '=', sta_marc_id)])
        self.assertEqual(len(mandate_ids), 1)

    def test_no_decision_date(self):
        '''
        Test the process of accepting states candidatures without decision date
        '''
        cr, uid, context = self.cr, self.uid, {}
        candidature_pool = self.registry('sta.candidature')
        committee_pool = self.registry('sta.selection.committee')
        committee_id = self.ref('%s.sc_bourgmestre_huy' % self._module_ns)
        sta_marc_id = self.ref('%s.sta_marc_bourgmestre' % self._module_ns)

        candidature_pool.signal_workflow(cr,
                                         uid,
                                         [sta_marc_id],
                                         'button_suggest',
                                         context=context)

        self.assertRaises(orm.except_orm,
                          committee_pool.button_accept_candidatures,
                          self.cr,
                          self.uid,
                          [committee_id])

    def test_legislature_early_closing(self):
        '''
        Test the mass update of mandates if deadline date of legislature
        is changed
        '''
        cr, uid, context = self.cr, self.uid, {}
        legislature_obj = self.registry['legislature']
        mandate_obj = self.registry['sta.mandate']
        legislature_id = self.ref('%s.legislature_01' % self._module_ns)
        mandate_id = self.ref('%s.stam_pauline_bourgmestre' % self._module_ns)

        self.assertRaises(orm.except_orm,
                          legislature_obj.write,
                          cr,
                          uid,
                          legislature_id,
                          {'deadline_date': '2015-01-01'})
        new_deadline_date = '2020-12-02'
        legislature_obj.write(cr, uid, legislature_id, {'deadline_date':
                                                        new_deadline_date},
                              context=context)
        mandate = mandate_obj.browse(cr, uid, mandate_id, context=context)
        legislature = legislature_obj.browse(cr, uid, legislature_id,
                                             context=context)
        self.assertEquals(legislature.deadline_date, new_deadline_date)
        self.assertEquals(mandate.deadline_date, new_deadline_date)
