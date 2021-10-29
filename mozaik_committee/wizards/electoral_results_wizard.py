# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast
import base64
import csv
from io import StringIO

from odoo import _, api, fields, models

file_import_structure = [
    "district",
    "E/S",
    "name",
    "votes",
    "position",
    "position_non_elected",
]


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class ElectoralResultsWizard(models.TransientModel):
    _name = "electoral.results.wizard"
    _description = "Electoral Results Wizard"

    legislature_id = fields.Many2one(comodel_name="legislature", string="Legislature")
    source_file = fields.Binary(string="Source File")
    error_lines = fields.One2many(
        comodel_name="electoral.results.wizard.errors",
        inverse_name="wizard_id",
        string="Errors",
    )
    file_lines = fields.One2many(
        comodel_name="electoral.results.wizard.lines",
        inverse_name="wizard_id",
        string="File Lines",
    )

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        """
        res = super().default_get(fields)
        context = self.env.context

        model = context.get("active_model", False)
        if not model:
            return res

        ids = (
            context.get("active_ids")
            or (context.get("active_id") and [context.get("active_id")])
            or []
        )

        legislature = self.env[model].browse(ids[0])
        res["legislature_id"] = legislature.id

        return res

    def validate_file(self):  # noqa: C901
        def save_error():
            error_obj.create(
                {
                    "wizard_id": self.id,
                    "line_number": line_number,
                    "error_msg": error_msg,
                }
            )

        self.ensure_one()

        district_obj = self.env["electoral.district"]
        candi_obj = self.env["sta.candidature"]
        error_obj = self.env["electoral.results.wizard.errors"]
        line_obj = self.env["electoral.results.wizard.lines"]
        source_file = base64.b64decode(self.source_file).decode("utf-8")
        csv_reader = csv.reader(StringIO(source_file))
        known_districts = {}

        line_number = 0
        for line in csv_reader:
            line_number += 1
            error_msg = False
            if line == "":
                continue

            if len(line) != len(file_import_structure):
                error_msg = _(
                    "Wrong number of columns(%s), "
                    "%s expected!" % (len(line), len(file_import_structure))
                )
                save_error()
                continue

            if line_number == 1:
                continue

            district = line[0]
            e_s = line[1]
            name = line[2]
            votes = line[3]
            position = line[4]
            position_non_elected = line[5] or 0

            if not is_integer(votes):
                error_msg = _("Votes value should be integer: %s" % votes)
                save_error()
                continue

            if position:
                if not is_integer(position):
                    error_msg = _("Position value should be integer: %s" % position)
                    save_error()
                    continue

            if position_non_elected:
                if not is_integer(position_non_elected):
                    error_msg = _(
                        "Position non elected value should "
                        "be integer: %s" % position_non_elected
                    )
                    save_error()
                    continue

            district_id = False
            if district not in known_districts:
                district_id = district_obj.search([("name", "=", district)], limit=1)
                if not district_id:
                    error_msg = _("Unknown district: %s" % district)
                    save_error()
                    continue
                else:
                    known_districts[name] = district_id.id

            candidature_id = candi_obj.search(
                [
                    ("partner_id", "=", name),
                    ("electoral_district_id", "=", district_id.id),
                    ("legislature_id", "=", self.legislature_id.id),
                    ("active", "<=", True),
                ],
                limit=1,
            )

            if not candidature_id:
                error_msg = _("Unknown candidate: %s" % name)
                save_error()
                continue

            candidature = candi_obj.browse(candidature_id.id)

            if not e_s:
                if candidature.is_effective or candidature.is_substitute:
                    value = "E" if candidature.is_effective else "S"
                    error_msg = _(
                        "Candidature: inconsistent value for "
                        "column E/S: should be %s" % value
                    )
                    save_error()
                    continue
                if position and position_non_elected:
                    value = "E" if candidature.is_effective else "S"
                    error_msg = _(
                        "Position(%s) and position non elected(%s)"
                        " can not be set both" % (position, position_non_elected)
                    )
                    save_error()
                    continue

            elif e_s == "E":
                if not candidature.is_effective:
                    error_msg = _("Candidature is not flagged as effective")
                    save_error()
                    continue

            elif e_s == "S":
                if not candidature.is_substitute:
                    error_msg = _("Candidature is not flagged as substitute")
                    save_error()
                    continue
            else:
                error_msg = _("Inconsistent value for column E/S: %s" % e_s)
                save_error()
                continue

            if e_s and position_non_elected:
                error_msg = _(
                    "Position non elected is incompatible" " with e_s value: %s" % e_s
                )
                save_error()
                continue

            if candidature.state == "designated":
                pass
            elif candidature.state == "elected":
                if int(position_non_elected) > 0:
                    error_msg = _(
                        "Candidate is elected but position "
                        "non elected (%s) is set" % position_non_elected
                    )
                    save_error()
                    continue
            elif candidature.state == "non-elected":
                pass
            else:
                error_msg = _(
                    "Inconsistent state for candidature: %s" % candidature.state
                )
                save_error()
                continue

            line_obj.create(
                {
                    "wizard_id": self.id,
                    "sta_candidature_id": candidature.id,
                    "data": str(line),
                }
            )

        return {
            "type": "ir.actions.act_window",
            "name": _("Import Electoral Results"),
            "res_model": "electoral.results.wizard",
            "view_mode": "form",
            "target": "new",
            "view_id": self.env.ref(
                "mozaik_committee.electoral_results_wizard_step2"
            ).id,
            "res_id": self.id,
        }

    def import_file(self):
        self.ensure_one()

        for line in self.file_lines:
            candi_obj = self.env["sta.candidature"]
            file_line = ast.literal_eval(line.data)

            e_s = file_line[1]
            votes = file_line[3]
            position = file_line[4]
            position_non_elected = file_line[5]

            position_col = "election_effective_position"
            votes_col = "effective_votes"

            sc_event = "button_elected"

            if not e_s and position_non_elected:
                position = position_non_elected
                e_s = "S"

            if e_s == "S":
                position_col = "election_substitute_position"
                votes_col = "substitute_votes"
                if not line.sta_candidature_id.is_effective:
                    sc_event = "button_non_elected"
                else:
                    sc_event = False

            if e_s == "E":
                if not position or int(position) == 0:
                    sc_event = "button_non_elected"

            vals = {position_col: position, votes_col: votes}

            candi_obj.browse(line.sta_candidature_id.id).write(vals)

            if line.sta_candidature_id.state == "designated" and sc_event:
                getattr(line.sta_candidature_id, sc_event)()


class ElectoralResultsWizardErrors(models.TransientModel):
    _name = "electoral.results.wizard.errors"
    _description = "Electoral Results Wizard Errors"

    wizard_id = fields.Many2one(
        comodel_name="electoral.results.wizard",
        string="Wizard",
    )
    line_number = fields.Integer(string="Line Number")
    error_msg = fields.Text(string="Message")


class ElectoralResultsWizardLines(models.TransientModel):
    _name = "electoral.results.wizard.lines"
    _description = "Electoral Results Wizard Lines"

    wizard_id = fields.Many2one(
        comodel_name="electoral.results.wizard",
        string="Wizard",
    )
    sta_candidature_id = fields.Many2one(
        comodel_name="sta.candidature",
        string="Candidature",
    )
    data = fields.Text(string="File Values")
