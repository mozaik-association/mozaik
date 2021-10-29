# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
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
        self.int_paul_id.button_reject()
        self.assertEqual(self.int_paul_id.state, "rejected")

        # Thierry is suggested again
        self.int_thierry_secretaire_id.button_suggest()
        self.assertEqual(self.int_thierry_secretaire_id.state, "suggested")

        # Accept Candidatures
        self.committee_id.write({"decision_date": "2014-04-01"})
        self.committee_id.button_accept_candidatures()
        self.assertEqual(self.int_thierry_secretaire_id.state, "elected")
        self.assertEqual(self.int_paul_id.state, "rejected")

        # Mandate is automatically created for Thierry candidature
        #                                - mandate is linked to candidature
        mandate_ids = self.env["int.mandate"].search(
            [("candidature_id", "in", candidature_ids.ids)]
        )
        self.assertEqual(len(mandate_ids), 1)

    def test_no_decision_date(self):
        """
        Test the process of accepting internal candidatures without decision
        date
        """
        self.int_thierry_secretaire_id.button_suggest()
        self.int_paul_id.button_reject()
        with self.assertRaises(ValidationError):
            self.committee_id.button_accept_candidatures()
