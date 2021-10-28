# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStaMandate(TransactionCase):
    def setUp(self):
        super(TestStaMandate, self).setUp()
        self.committee_id = self.env.ref("mozaik_committee.sc_tete_huy_communale")
        self.sta_paul_id = self.env.ref("mozaik_committee.sta_paul_communal")
        self.sta_thierry_id = self.env.ref("mozaik_committee.sta_thierry_communal")
        self.committee_id.decision_date = False

    def test_sta_candidature_process(self):
        """
        Test the process of state candidatures until mandate creation
        """
        candidature_ids = self.sta_thierry_id | self.sta_paul_id

        # Thierry candidature is rejected
        self.sta_thierry_id.button_reject()
        self.assertEqual(self.sta_thierry_id.state, "rejected")

        # Thierry candidature is set back to declare
        self.sta_thierry_id.button_declare()
        self.assertEqual(self.sta_thierry_id.state, "declared")

        # Candidatures are designated
        self.committee_id.button_designate_candidatures()
        for candidature in candidature_ids:
            self.assertEqual(candidature.state, "designated")

        # Paul candidature is set back to declare
        self.sta_paul_id.button_declare()
        self.assertEqual(self.sta_paul_id.state, "declared")

        # Accept Thierry candidature
        self.committee_id.write({"decision_date": "2014-04-01"})
        self.sta_thierry_id.button_elected()
        self.assertEqual(self.sta_thierry_id.state, "elected")

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
        # Attempt to accept candidatures before suggesting them
        self.assertRaises(orm.except_orm,
                          committee_pool.button_accept_candidatures,
                          cr,
                          uid,
                          [committee_id])

        # Paul, Pauline, Marc and Thierry candidatures are suggested
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

        # Candidatures are refused
        committee_pool.button_refuse_candidatures(self.cr,
                                                  self.uid,
                                                  [committee_id])
        for candidature_data in candidature_pool.read(self.cr,
                                                      self.uid,
                                                      candidature_ids,
                                                      ['state']):
            self.assertEqual(candidature_data['state'], 'declared')

        # Paul candidature is rejected
        candidature_pool.signal_workflow(cr,
                                         uid,
                                         [sta_paul_communal_id],
                                         'button_reject',
                                         context=context)
        self.assertEqual(candidature_pool.read(self.cr,
                                               self.uid,
                                               sta_paul_communal_id,
                                               ['state'])['state'], 'rejected')

        # Pauline, Marc and Thierry candidatures are suggested again
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

        # Accept Candidatures
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

        # Result of election:
        #                    - Pauline is not elected
        #                    - Marc and Thierry are elected
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

        # Create Mandates for elected candidatures:
        #                             - mandates are linked to candidatures
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

        # Non elect others
        self.committee_id.button_non_elect_candidatures()
        self.assertEqual(self.sta_paul_id.state, "non-elected")
        self.assertEqual(self.sta_thierry_id.state, "elected")

    def test_no_decision_date(self):
        """
        Test the process of (non-)electing state candidatures without decision
        date
        """
        with self.assertRaises(ValidationError):
            self.committee_id.button_non_elect_candidatures()
