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

        # Accept Thierry candidature
        self.committee_id.write({"decision_date": "2014-04-01"})
        self.sta_thierry_id.button_elected()
        self.assertEqual(self.sta_thierry_id.state, "elected")

        # Mandate is automatically created for Thierry candidature
        #                                - mandate is linked to candidature
        mandate_ids = self.env["sta.mandate"].search(
            [("candidature_id", "in", candidature_ids.ids)]
        )
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
        self.committee_id.button_designate_candidatures()
        with self.assertRaises(ValidationError):
            self.committee_id.button_non_elect_candidatures()
