# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestStaMandate(TransactionCase):
    def test_sta_candidature_legislative_process(self):
        """
        Test the process of states candidatures for a legislative assembly
        until mandate creation
        """
        committee_id = self.env.ref("mozaik_committee.sc_tete_huy_communale")
        sta_paul_communal_id = self.env.ref("mozaik_committee.sta_paul_communal")
        sta_pauline_communal_id = self.env.ref("mozaik_committee.sta_pauline_communal")
        sta_marc_communal_id = self.env.ref("mozaik_committee.sta_marc_communal")
        sta_thierry_communal_id = self.env.ref("mozaik_committee.sta_thierry_communal")
        sta_jacques_communal_id = self.env.ref("mozaik_committee.sta_jacques_communal")
        candidature_ids = (
            sta_paul_communal_id
            | sta_pauline_communal_id
            | sta_marc_communal_id
            | sta_thierry_communal_id
            | sta_jacques_communal_id
        )
        # Attempt to accept candidatures before suggesting them
        with self.assertRaises(UserError):
            committee_id.button_accept_candidatures()

        # Paul, Pauline, Marc, Thierry and Jacques candidatures are suggested
        candidature_ids.button_suggest()
        for candidature in candidature_ids:
            self.assertEqual(candidature.state, "suggested")

        # Candidatures are refused
        committee_id.button_refuse_candidatures()
        for candidature in candidature_ids:
            self.assertEqual(candidature.state, "declared")

        # Paul candidature is rejected
        sta_paul_communal_id.button_reject()
        self.assertEqual(sta_paul_communal_id.state, "rejected")

        # Pauline, Marc, Thierry and Jacques candidatures are suggested again
        candidature_ids = (
            sta_pauline_communal_id
            | sta_marc_communal_id
            | sta_thierry_communal_id
            | sta_jacques_communal_id
        )
        candidature_ids.button_suggest()
        for candidature in candidature_ids:
            self.assertEqual(candidature.state, "suggested")

        # Accept Candidatures
        committee_id.write({"decision_date": "2014-04-01"})
        committee_id.button_accept_candidatures()
        for candidature in candidature_ids:
            self.assertEqual(candidature.state, "designated")

        # Result of election:
        #                    - Pauline is not elected
        #                    - Marc, Thierry and Jacques are elected
        non_elected_ids = sta_pauline_communal_id
        elected_ids = (
            sta_marc_communal_id | sta_thierry_communal_id | sta_jacques_communal_id
        )
        non_elected_ids.button_non_elected()

        for candidature in non_elected_ids:
            self.assertEqual(candidature.state, "non-elected")

        elected_ids.button_elected()
        for candidature in elected_ids:
            self.assertEqual(candidature.state, "elected")

        # Create Mandates for elected candidatures:
        #                             - mandates are linked to candidatures
        elected_ids.button_create_mandate()
        mandate_ids = self.env["sta.mandate"].search(
            [("candidature_id", "in", elected_ids.ids)]
        )
        self.assertEqual(len(mandate_ids), len(elected_ids))

    def test_sta_candidature_not_legislative_process(self):
        """
        Test the process of states candidatures for a non legislative assembly
        until mandate creation
        """
        committee_id = self.env.ref("mozaik_committee.sc_bourgmestre_huy")
        sta_marc_id = self.env.ref("mozaik_committee.sta_marc_bourgmestre")

        sta_marc_id.button_suggest()
        self.assertEqual(sta_marc_id.state, "suggested")

        committee_id.write({"decision_date": "2014-04-01"})
        committee_id.button_accept_candidatures()
        self.assertEqual(sta_marc_id.state, "elected")
        mandate_ids = self.env["sta.mandate"].search(
            [("candidature_id", "=", sta_marc_id.id)]
        )
        self.assertEqual(len(mandate_ids), 1)

    def test_no_decision_date(self):
        """
        Test the process of accepting states candidatures without decision date
        """
        committee_id = self.env.ref("mozaik_committee.sc_bourgmestre_huy")
        sta_marc_id = self.env.ref("mozaik_committee.sta_marc_bourgmestre")

        sta_marc_id.button_suggest()
        with self.assertRaises(ValidationError):
            committee_id.button_accept_candidatures()
