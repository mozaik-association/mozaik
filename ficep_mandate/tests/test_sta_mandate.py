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
import logging
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.osv import orm

_logger = logging.getLogger(__name__)


class test_sta_mandate(SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        '../../ficep_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'ficep_mandate'

    def setUp(self):
        super(test_sta_mandate, self).setUp()

    def test_duplicate_sta_candidature_in_same_category(self):
        '''
        Try to create twice a candidature in the same category for a partner
        '''
        jacques_partner_id = self.ref('%s.res_partner_jacques' % self._module_ns)
        conseil_comm_cat_id = self.ref('%s.mc_conseiller_communal' % self._module_ns)
        selection_committee_id = self.ref('%s.sc_tete_huy_communale' % self._module_ns)

        committee = self.registry('selection.committee').browse(self.cr, self.uid, selection_committee_id)

        data = dict(mandate_category_id=conseil_comm_cat_id,
            selection_committee_id=selection_committee_id,
            designation_int_assembly_id=committee.designation_int_assembly_id.id,
            legislature_id=committee.legislature_id.id,
            electoral_district_id=committee.electoral_district_id.id,
            sta_assembly_id=committee.sta_assembly_id.id,
            partner_id=jacques_partner_id)

        self.registry('sta.candidature').create(self.cr, self.uid, data)
        self.assertRaises(orm.except_orm, self.registry('sta.candidature').create, self.cr, self.uid, data)

    def test_sta_candidature_legislative_process(self):
        '''
        Test the process of states candidatures for a legislative assembly until mandate creation
        '''
        candidature_pool = self.registry('sta.candidature')
        mandate_pool = self.registry('sta.mandate')
        committee_pool = self.registry('selection.committee')
        committee_id = self.ref('%s.sc_tete_huy_communale' % self._module_ns)
        sta_paul_communal_id = self.ref('%s.sta_paul_communal' % self._module_ns)
        sta_pauline_communal_id = self.ref('%s.sta_pauline_communal' % self._module_ns)
        sta_marc_communal_id = self.ref('%s.sta_marc_communal' % self._module_ns)
        sta_thierry_communal_id = self.ref('%s.sta_thierry_communal' % self._module_ns)

        candidature_ids = [sta_paul_communal_id, sta_pauline_communal_id, sta_marc_communal_id, sta_thierry_communal_id]
        '''
           Attempt to accept candidatures before suggesting them
        '''
        self.assertRaises(orm.except_orm, committee_pool.button_accept_candidatures, self.cr, self.uid, [committee_id])

        '''
            Paul, Pauline, Marc and Thierry candidatures are suggested
        '''
        candidature_pool.signal_button_suggest(self.cr, self.uid, candidature_ids)

        for candidature_data in candidature_pool.read(self.cr, self.uid, candidature_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'suggested')

        '''
            Candidatures are refused
        '''
        committee_pool.button_reject_candidatures(self.cr, self.uid, [committee_id])
        for candidature_data in candidature_pool.read(self.cr, self.uid, candidature_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'declared')

        '''
            Paul candidature is rejected
        '''
        candidature_pool.signal_button_reject(self.cr, self.uid, [sta_paul_communal_id])
        self.assertEqual(candidature_pool.read(self.cr, self.uid, sta_paul_communal_id, ['state'])['state'], 'rejected')

        '''
            Pauline, Marc and Thierry candidatures are suggested again
        '''
        candidature_ids = [sta_pauline_communal_id, sta_marc_communal_id, sta_thierry_communal_id]
        candidature_pool.signal_button_suggest(self.cr, self.uid, candidature_ids)

        for candidature_data in candidature_pool.read(self.cr, self.uid, candidature_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'suggested')

        '''
            Candidatures are accepted
        '''
        committee_pool.button_accept_candidatures(self.cr, self.uid, [committee_id])
        for candidature_data in candidature_pool.read(self.cr, self.uid, candidature_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'designated')

        '''
            Result of election:
                            - Pauline is not elected
                            - Marc and Thierry are elected
        '''
        non_elected_ids = [sta_pauline_communal_id]
        elected_ids = [sta_marc_communal_id, sta_thierry_communal_id]

        candidature_pool.signal_button_non_elected(self.cr, self.uid, non_elected_ids)
        for candidature_data in candidature_pool.read(self.cr, self.uid, non_elected_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'non-elected')

        candidature_pool.signal_button_elected(self.cr, self.uid, elected_ids)
        for candidature_data in candidature_pool.read(self.cr, self.uid, elected_ids, ['state']):
            self.assertEqual(candidature_data['state'], 'elected')

        '''
            Create Mandates for elected candidatures:
                                                - candidatures are inactivated
                                                - mandates are linked to candidatures
        '''
        candidature_pool.button_create_mandate(self.cr, self.uid, elected_ids)
        for candidature_data in candidature_pool.read(self.cr, self.uid, elected_ids, ['active']):
            self.assertEqual(candidature_data['active'], False)

        mandate_ids = mandate_pool.search(self.cr, self.uid, [('candidature_id', 'in', elected_ids)])
        self.assertEqual(len(mandate_ids), len(elected_ids))

    def test_sta_candidature_not_legislative_process(self):
        '''
        Test the process of states candidatures for a non legislative assembly until mandate creation
        '''
        candidature_pool = self.registry('sta.candidature')
        mandate_pool = self.registry('sta.mandate')
        committee_pool = self.registry('selection.committee')
        committee_id = self.ref('%s.sc_bourgmestre_huy' % self._module_ns)
        sta_marc_id = self.ref('%s.sta_marc_bourgmestre' % self._module_ns)

        candidature_pool.signal_button_suggest(self.cr, self.uid, [sta_marc_id])

        candidature_data = candidature_pool.read(self.cr, self.uid, sta_marc_id, ['state'])
        self.assertEqual(candidature_data['state'], 'suggested')

        committee_pool.button_accept_candidatures(self.cr, self.uid, [committee_id])
        candidature_data = candidature_pool.read(self.cr, self.uid, sta_marc_id, ['state'])
        self.assertEqual(candidature_data['state'], 'elected')

        mandate_ids = mandate_pool.search(self.cr, self.uid, [('candidature_id', '=', sta_marc_id)])
        self.assertEqual(len(mandate_ids), 1)
