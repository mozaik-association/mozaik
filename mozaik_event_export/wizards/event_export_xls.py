# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, fields, models


class EventExportXls(models.TransientModel):

    _name = "event.export.xls"
    _inherit = "ama.abstract.export"
    _description = "Event Export xls"

    event_id = fields.Many2one(comodel_name="event.event", required=True)
    export_file = fields.Binary(
        string="Excel File",
        readonly=True,
    )
    export_filename = fields.Char(
        string="Export xls filename",
    )

    def _get_interests(self):
        self.ensure_one()
        return ", ".join(self.event_id.interest_ids.mapped("name"))

    def _add_questions_to_cols(self, header):
        """
        header: list of str

        Adds in header columns labels for each question
        """
        self.ensure_one()
        event = self.event_id
        for question in event.question_ids:
            header.append(question.title)

    def _get_headers(self):
        """
        Get the columns (header) for event registrations
        :return: list of str
        """
        header = super()._get_headers()
        header += [
            _("Object Type"),
            _("Object Name"),
            _("Interests"),
            _("Answering Partner"),
            _("Partner ID"),
            _("Partner URL"),
            _("Registration URL"),
            _("Create Date"),
            _("Last Update Date"),
            _("Status"),
            _("Lastname"),
            _("Firstname"),
            _("Gender"),
            _("Birth Date"),
            _("Age"),
            _("Membership State"),
            _("Email"),
            _("Mobile"),
            _("Street"),
            _("Zip"),
            _("City"),
        ]
        self._add_questions_to_cols(header)
        return header

    @api.model
    def _get_row_values(self, values):
        """
        Get the values of the specified object
        :param values: dict
        :return: list of str that corresponds to a row of the file
        """
        export_values = super()._get_row_values(values)
        keys = [
            "object_type",
            "object_name",
            "interests",
            "answering_partner",
            "partner_id",
            "partner_url",
            "event_registration_url",
            "create_date",
            "write_date",
            "event_status",
            "lastname",
            "firstname",
            "gender",
            "birthdate_date",
            "age",
            "membership_state",
            "email",
            "mobile",
            "street",
            "zip",
            "city",
        ]
        export_values += [values.get(k, "") for k in keys]
        export_values += values.get("answers", [])
        return export_values

    def _get_select(self):
        """
        Return select part of the query
        """
        return """
        SELECT
        p.lastname,
        p.firstname,
        p.identifier as number,
        p.id as partner_id,
        p.gender,
        p.birthdate_date,
        p.membership_state_id as membership_state,
        p.email,
        p.mobile,
        p.street,
        p.zip,
        p.city,
        er.id as event_registration_id,
        er.create_date,
        er.write_date,
        er.state as event_status
        """

    def _get_from(self):
        """
        Return from part of the query
        """
        return """
        FROM event_registration er
        LEFT JOIN res_partner p ON er.associated_partner_id = p.id
        """

    def _get_where(self, model_ids):
        """
        Return where part of the query
        """
        where_values = {
            "model_ids": tuple(model_ids),
        }
        return self.env.cr.mogrify("""er.id IN %(model_ids)s""", where_values)

    def _compute_answer(self, lines):
        """
        We always have to complete exactly 1 column.

        Possibilities:
        * len(lines) == 0: no answer for this question
        * len(lines) == 1: this question has been answered
        """
        answer = ""
        if len(lines) == 1:
            if lines.question_type == "simple_choice":
                answer = lines.value_answer_id.name
            elif lines.question_type == "text_box":
                answer = lines.value_text_box

        return answer

    def _give_answers(self, event_registration_id):
        """
        Returns a list of strings (answers).
        We take each question at one time, and we write the answers in the right column.
        """
        if not event_registration_id:
            return False
        answers = []
        event_registration = self.env["event.registration"].browse(
            event_registration_id
        )

        for question in event_registration.event_id.question_ids:
            lines = event_registration.registration_answer_ids.filtered(
                lambda line: line.question_id == question
            )
            answers.append(self._compute_answer(lines))

        return answers

    def _get_event_registration_url(self, event_registration_id):
        """
        Returns the Odoo URL to access the event registration form view
        using the given id.
        """
        if not event_registration_id:
            return ""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        custom_url = (
            "/web#id=%(event_registration_id)d&action=%(action_id)d&active_id="
            "%(event_id)d&model=event.registration&view_type=form&"
            "cids=&menu_id=%(menu_id)d"
            % {
                "event_registration_id": event_registration_id,
                "event_id": self.event_id.id,
                "action_id": self.env.ref("event.action_registration").id,
                "menu_id": self.env.ref("event.event_main_menu").id,
            }
        )
        return base_url + custom_url

    def _get_selections(self):
        """
        Build a dictionary with all membership states,
        all event_states and all genders.
        """
        selections = super()._get_selections()
        selections_event_reg = self.env["event.registration"].fields_get(
            allfields=["state"]
        )
        selections["event_states"] = {
            k: v for k, v in selections_event_reg["state"]["selection"]
        }
        return selections

    def _update_data(self, data, selections):
        """
        Update data and return export values

        NOTE:
            * We select event title here, to take the translated version
            * As age is not stored, we cannot find it in the sql query

        :data: dict containing the data to format for export
        :selections: dict containing all possible values for some selection fields
        """
        partner_id = data.get("partner_id", False)
        data.update(
            {
                "object_type": "Event",
                "object_name": self.event_id.name,
                "interests": self._get_interests(),
                "answering_partner": self._compute_answering_partner(
                    data.get("number", "0"),
                    data.get("lastname", False),
                    data.get("firstname", False),
                ),
                "event_status": selections.get("event_states", {}).get(
                    data.get("event_status"), data.get("event_status")
                ),
                "age": self.env["res.partner"].browse(partner_id).age
                if partner_id
                else 0,
                "membership_state": selections.get("membership_states", {}).get(
                    data.get("membership_state"), data.get("membership_state")
                ),
                "gender": selections.get("genders", {}).get(
                    data.get("gender"), data.get("gender")
                ),
                "answers": self._give_answers(data.get("event_registration_id", False)),
                "partner_url": self._get_partner_url(partner_id),
                "event_registration_url": self._get_event_registration_url(
                    data.get("event_registration_id", False)
                ),
            }
        )
        return data

    def _export(self):
        """
        Export the specified coordinates to a xls file.
        """
        if not self.event_id:
            return
        targets = self.env["event.registration"].search(
            [("event_id", "=", self.event_id.id)]
        )
        content = self._get_xls(targets.ids)
        content = base64.encodebytes(content)
        self.write(
            {
                "export_file": content,
                "export_filename": "extract.xls",
            }
        )

    def export(self):
        self._export()
        action = self.event_id.export_action()
        action.update(
            {
                "res_id": self.id,
                "target": "new",
            }
        )
        return action
