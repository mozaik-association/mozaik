# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestIntMandate(TransactionCase):
    def setUp(self):
        super(TestIntMandate, self).setUp()
        self.committee_id = self.env.ref("mozaik_committee.sc_secretaire_regional")
        self.int_paul_id = self.env.ref("mozaik_committee.int_paul_secretaire")
        self.int_thierry_secretaire_id = self.env.ref(
            "mozaik_committee.int_thierry_secretaire"
        )

    def test_int_candidature_process(self):
        """
        Test the process of internal candidatures until mandate creation
        """
        candidature_ids = self.int_thierry_secretaire_id | self.int_paul_id

        # Thierry candidature is rejected
        self.int_thierry_secretaire_id.button_reject()
        self.assertEqual(self.int_thierry_secretaire_id.state, "rejected")

        # Thierry candidature is set back to declare
        self.int_thierry_secretaire_id.button_declare()
        self.assertEqual(self.int_thierry_secretaire_id.state, "declared")

        # Candidatures are designated
        self.committee_id.button_designate_candidatures()
        for candidature in candidature_ids:
            self.assertEqual(candidature.state, "designated")

        # Paul candidature is set back to declare
        self.int_paul_id.button_declare()
        self.assertEqual(self.int_paul_id.state, "declared")

        # Accept Thierry candidature
        self.committee_id.write({"decision_date": "2014-04-01"})
        self.int_thierry_secretaire_id.button_elected()
        self.assertEqual(self.int_thierry_secretaire_id.state, "elected")

        # Mandate is automatically created for Thierry candidature
        #                                - mandate is linked to candidature
        mandate_ids = self.env["int.mandate"].search(
            [("candidature_id", "in", candidature_ids.ids)]
        )
        self.assertEqual(len(mandate_ids), 1)

        # Non elect others
        self.committee_id.button_non_elect_candidatures()
        self.assertEqual(self.int_paul_id.state, "non-elected")
        self.assertEqual(self.int_thierry_secretaire_id.state, "elected")

    def test_no_decision_date(self):
        """
        Test the process of (non-)electing internal candidatures without decision
        date
        """
        with self.assertRaises(ValidationError):
            self.committee_id.button_non_elect_candidatures()
