# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestExtMandate(TransactionCase):

    def setUp(self):
        super(TestExtMandate, self).setUp()
        self.committee_id = self.env.ref('mozaik_committee.sc_membre_effectif_ag')
        self.ext_paul_id = self.env.ref('mozaik_committee.ext_paul_membre_ag')
        self.ext_thierry_id = self.env.ref('mozaik_committee.ext_thierry_membre_ag')

    def test_ext_candidature_process(self):
        '''
        Test the process of internal candidatures until mandate creation
        '''
        candidature_ids = self.ext_thierry_id | self.ext_paul_id
        # Attempt to accept candidatures before suggesting them
        with self.assertRaises(UserError):
            self.committee_id.button_accept_candidatures()

        # Paul and Thierry are suggested
        candidature_ids.button_suggest()

        # Candidatures are refused
        self.committee_id.button_refuse_candidatures()
        for candidature in candidature_ids:
            self.assertEqual(candidature.state, "declared")

        # Paul candidature is rejected
        self.ext_paul_id.button_reject()
        self.assertEqual(self.ext_paul_id.state, "rejected")

        # Thierry is suggested again
        self.ext_thierry_id.button_suggest()
        self.assertEqual(self.ext_thierry_id.state, "suggested")

        # Accept Candidatures
        self.committee_id.write({'decision_date': '2014-04-01'})
        self.committee_id.button_accept_candidatures()
        self.assertEqual(self.ext_thierry_id.state, "elected")
        self.assertEqual(self.ext_paul_id.state, "rejected")

        # Mandate is automatically created for Thierry candidature
        #                                - mandate is linked to candidature
        mandate_ids = self.env["ext.mandate"].search(
            [("candidature_id", "in", candidature_ids.ids)]
        )
        self.assertEqual(len(mandate_ids), 1)

    def test_no_decision_date(self):
        '''
        Test the process of accepting internal candidatures without decision
        date
        '''
        self.ext_thierry_id.button_suggest()
        self.ext_paul_id.button_reject()
        with self.assertRaises(ValidationError):
            self.committee_id.button_accept_candidatures()
