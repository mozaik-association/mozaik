# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import tempfile

from odoo import _
from odoo.tests.common import TransactionCase

from ..wizards.electoral_results_wizard import file_import_structure


class TestElectoralResultsWizard(TransactionCase):
    def setUp(self):
        super(TestElectoralResultsWizard, self).setUp()
        self.district = self.env.ref("mozaik_structure.electoral_district_02")
        self.legislature = self.env.ref("mozaik_mandate.legislature_02")
        self.sta_paul_communal = self.env.ref("mozaik_committee.sta_paul_communal")
        self.sta_pauline_communal = self.env.ref(
            "mozaik_committee.sta_pauline_communal"
        )
        self.sta_marc_communal = self.env.ref("mozaik_committee.sta_marc_communal")
        self.sta_thierry_communal = self.env.ref(
            "mozaik_committee.sta_thierry_communal"
        )
        self.sta_jacques_communal = self.env.ref(
            "mozaik_committee.sta_jacques_communal"
        )

        self.committee_id = self.env.ref("mozaik_committee.sc_tete_huy_communale")

        accepted_ids = (
            self.sta_paul_communal
            | self.sta_pauline_communal
            | self.sta_thierry_communal
            | self.sta_jacques_communal
        )
        rejected_ids = self.sta_marc_communal

        accepted_ids.button_suggest()
        rejected_ids.button_reject()

        self.committee_id.write({"decision_date": "2014-04-01"})
        self.committee_id.button_accept_candidatures()

    def test_electoral_results_wizard_wrong_file(self):
        """
        Import electoral results
        """
        self.sta_paul_communal.button_elected()

        temp_file = tempfile.SpooledTemporaryFile(mode="w+r")
        temp_file.write(",".join(file_import_structure) + "\n")
        # wrong row size
        data = ["a", "b"]
        temp_file.write(",".join(data) + "\n")
        # votes non numerical
        data = ["test", "", "Toto", "a", "", ""]
        temp_file.write(",".join(data) + "\n")
        # position non numerical
        data = ["test", "", "Toto", "3", "a", ""]
        temp_file.write(",".join(data) + "\n")
        # position non elected non numerical
        data = ["test", "", "Toto", "3", "2", "a"]
        temp_file.write(",".join(data) + "\n")
        # unknown district
        data = ["test", "", "Toto", "3", "2", "1"]
        temp_file.write(",".join(data) + "\n")
        # unknown candidate
        data = [self.district.name, "", "Toto", "3", "2", ""]
        temp_file.write(",".join(data) + "\n")
        # bad candidature state
        data = [
            self.district.name,
            "",
            self.sta_marc_communal.partner_id.name,
            "3",
            "2",
            "",
        ]
        temp_file.write(",".join(data) + "\n")
        # elected candidate with position non elected set
        data = [
            self.district.name,
            "",
            self.sta_paul_communal.partner_id.name,
            "3",
            "",
            "1",
        ]
        temp_file.write(",".join(data) + "\n")
        # inconsistent value for column E/S
        data = [
            self.district.name,
            "B",
            self.sta_pauline_communal.partner_id.name,
            "3",
            "2",
            "1",
        ]
        temp_file.write(",".join(data) + "\n")
        # inconsistent value for column E/S with candidature settings
        data = [
            self.district.name,
            "",
            self.sta_thierry_communal.partner_id.name,
            "3",
            "2",
            "1",
        ]
        temp_file.write(",".join(data) + "\n")
        # Effective line with substitute candidature
        data = [
            self.district.name,
            "E",
            self.sta_thierry_communal.partner_id.name,
            "3",
            "2",
            "1",
        ]
        temp_file.write(",".join(data) + "\n")
        # Substitute line with effective candidature
        data = [
            self.district.name,
            "S",
            self.sta_pauline_communal.partner_id.name,
            "3",
            "2",
            "1",
        ]
        temp_file.write(",".join(data) + "\n")
        # Position non elected should not be set with e_S value
        data = [
            self.district.name,
            "E",
            self.sta_pauline_communal.partner_id.name,
            "3",
            "2",
            "1",
        ]
        temp_file.write(",".join(data) + "\n")
        # Position and position non elected can not be set both
        data = [
            self.district.name,
            "",
            self.sta_paul_communal.partner_id.name,
            "3",
            "2",
            "1",
        ]
        temp_file.write(",".join(data) + "\n")
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            "active_ids": [self.legislature.id],
            "active_model": "legislature",
        }
        wiz_id = (
            self.env["electoral.results.wizard"]
            .with_context(context)
            .create({"source_file": base64.b64encode(data_file.encode("utf-8"))})
        )
        wiz_id.validate_file()

        self.assertEqual(len(wiz_id.error_lines), 14)
        for error in wiz_id.error_lines:

            if error.line_number == 2:
                expected_msg = _("Wrong number of columns(%s), " "%s expected!") % (
                    2,
                    len(file_import_structure),
                )
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 3:
                expected_msg = _("Votes value should be integer: %s") % "a"
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 4:
                expected_msg = _("Position value should be integer: %s") % "a"
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 5:
                expected_msg = (
                    _("Position non elected value should " "be integer: %s") % "a"
                )
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 6:
                expected_msg = _("Unknown district: %s") % "test"
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 7:
                expected_msg = _("Unknown candidate: %s") % "Toto"
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 8:
                expected_msg = _("Inconsistent state for candidature: %s") % "rejected"
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 9:
                expected_msg = (
                    _("Candidate is elected but position " "non elected (%s) is set")
                    % "1"
                )
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 10:
                expected_msg = _("Inconsistent value for column E/S: %s") % "B"
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 11:
                expected_msg = (
                    _("Candidature: inconsistent value for " "column E/S: should be %s")
                    % "S"
                )
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 12:
                expected_msg = _("Candidature is not flagged as effective")
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 13:
                expected_msg = _("Candidature is not flagged as substitute")
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 14:
                expected_msg = (
                    _("Position non elected is incompatible " "with e_s value: %s")
                    % "E"
                )
                self.assertEqual(error.error_msg, expected_msg)

            elif error.line_number == 15:
                expected_msg = _(
                    "Position(%s) and position non elected(%s) " "can not be set both"
                ) % ("2", "1")
                self.assertEqual(error.error_msg, expected_msg)
            else:
                pass

    def test_electoral_results_wizard_elected(self):
        """
        Import electoral results
        """
        used = (
            self.sta_paul_communal
            | self.sta_pauline_communal
            | self.sta_jacques_communal
        )
        temp_file = tempfile.SpooledTemporaryFile(mode="w+r")
        temp_file.write(",".join(file_import_structure) + "\n")

        data = [
            self.district.name,
            "",
            self.sta_paul_communal.partner_id.name,
            "1258",
            "1",
            "",
        ]
        temp_file.write(",".join(data) + "\n")

        data = [
            self.district.name,
            "E",
            self.sta_pauline_communal.partner_id.name,
            "1258",
            "1",
            "",
        ]
        temp_file.write(",".join(data) + "\n")

        data = [
            self.district.name,
            "S",
            self.sta_jacques_communal.partner_id.name,
            "1258",
            "1",
            "",
        ]
        temp_file.write(",".join(data) + "\n")
        data = [
            self.district.name,
            "E",
            self.sta_jacques_communal.partner_id.name,
            "1258",
            "1",
            "",
        ]
        temp_file.write(",".join(data) + "\n")

        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            "active_ids": [self.legislature.id],
            "active_model": "legislature",
        }
        wiz_id = (
            self.env["electoral.results.wizard"]
            .with_context(context)
            .create(
                {"source_file": base64.b64encode(data_file.encode("utf-8"))},
            )
        )
        wiz_id.validate_file()

        self.assertEqual(len(wiz_id.error_lines), 0)

        wiz_id.import_file()

        for candidature in used:
            self.assertEqual(candidature.state, "elected")
            self.assertEqual(candidature.election_effective_position, 1)
            self.assertEqual(candidature.effective_votes, 1258)

    def test_electoral_results_wizard_non_elected(self):
        """
        Import electoral results
        """
        used = (
            self.sta_paul_communal
            | self.sta_pauline_communal
            | self.sta_jacques_communal
        )
        temp_file = tempfile.SpooledTemporaryFile(mode="w+r")
        temp_file.write(",".join(file_import_structure) + "\n")

        data = [
            self.district.name,
            "",
            self.sta_paul_communal.partner_id.name,
            "1258",
            "",
            "1",
        ]
        temp_file.write(",".join(data) + "\n")

        data = [
            self.district.name,
            "E",
            self.sta_pauline_communal.partner_id.name,
            "1258",
            "0",
            "",
        ]
        temp_file.write(",".join(data) + "\n")

        data = [
            self.district.name,
            "S",
            self.sta_jacques_communal.partner_id.name,
            "1258",
            "1",
            "",
        ]
        temp_file.write(",".join(data) + "\n")
        data = [
            self.district.name,
            "E",
            self.sta_jacques_communal.partner_id.name,
            "1258",
            "0",
            "",
        ]
        temp_file.write(",".join(data) + "\n")

        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            "active_ids": [self.legislature.id],
            "active_model": "legislature",
        }
        wiz_id = (
            self.env["electoral.results.wizard"]
            .with_context(context)
            .create(
                {"source_file": base64.b64encode(data_file.encode("utf-8"))},
            )
        )
        wiz_id.validate_file()

        self.assertEqual(len(wiz_id.error_lines), 0)

        wiz_id.import_file()

        for candidature in used:
            self.assertEqual(candidature.state, "non-elected")
            if candidature.id == self.sta_paul_communal.id:
                self.assertEqual(candidature.election_substitute_position, 1)
                self.assertEqual(candidature.substitute_votes, 1258)
            else:
                self.assertEqual(candidature.election_effective_position, 0)
                self.assertEqual(candidature.effective_votes, 1258)
