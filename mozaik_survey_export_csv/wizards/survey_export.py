# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, fields, models

SIMPLE_QUESTION_TYPES = ["text_box", "char_box", "numerical_box", "date", "datetime"]


class SurveyExport(models.TransientModel):

    _name = "survey.export"
    _inherit = "ama.abstract.export"
    _description = "Survey export"

    survey_id = fields.Many2one(comodel_name="survey.survey", required=True)
    export_file = fields.Binary(
        readonly=True,
    )
    export_filename = fields.Char()
    export_type = fields.Selection(
        [("xls", "Excel format"), ("csv", "CSV format")], default="xls", required=True
    )

    def _get_interests(self):
        self.ensure_one()
        return ", ".join(self.survey_id.interest_ids.mapped("name"))

    def _add_questions_to_cols(self, header):
        """
        header: list of str

        Adds in header columns labels for each question
        """
        self.ensure_one()
        survey = self.survey_id
        for question in survey.question_ids:
            if question.question_type in SIMPLE_QUESTION_TYPES + ["simple_choice"]:
                header.append(question.title)
            elif question.question_type == "multiple_choice":
                for sugg_answer in question.suggested_answer_ids:
                    header.append(question.title + " - " + sugg_answer.value)
            elif question.question_type == "matrix":
                question_title = question.title
                if question.matrix_subtype == "simple":
                    for row in question.matrix_row_ids:
                        row_title = row.value
                        header.append(question_title + ": " + row_title)
                elif question.matrix_subtype == "multiple":
                    for row in question.matrix_row_ids:
                        row_title = row.value
                        for sugg_answer in question.suggested_answer_ids:
                            sugg_title = sugg_answer.value
                            header.append(
                                question_title + ": " + row_title + " - " + sugg_title
                            )
            if question.comments_allowed and question.question_type in [
                "simple_choice",
                "multiple_choice",
                "matrix",
            ]:
                header.append(question.title + " " + _("(Comments)"))

    def _get_headers(self):
        """
        Get the columns (header) for survey answers
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
            _("Access Token"),
            _("Survey answer URL"),
            _("Create Date"),
            _("Last Update Date"),
            _("Status"),
            _("Lastname"),
            _("Firstname"),
            _("Gender"),
            _("Birth Date"),
            _("Membership State"),
            _("Email"),
            _("Mobile"),
            _("Street"),
            _("Zip"),
            _("City"),
            _("Score (%)"),
            _("Quizz passed"),
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
            "access_token",
            "user_input_url",
            "create_date",
            "write_date",
            "survey_status",
            "lastname",
            "firstname",
            "gender",
            "birthdate_date",
            "membership_state",
            "email",
            "mobile",
            "street",
            "zip",
            "city",
            "score",
            "scoring_success",
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
        ui.id as user_input_id,
        ui.access_token,
        ui.create_date,
        ui.write_date,
        ui.state as survey_status,
        ui.scoring_percentage as score,
        ui.scoring_success
        """

    def _get_from(self):
        """
        Return from part of the query
        """
        return """
        FROM survey_user_input ui
        LEFT JOIN res_partner p ON ui.partner_id = p.id
        """

    def _get_where(self, model_ids):
        """
        Return where part of the query
        """
        where_values = {
            "model_ids": tuple(model_ids),
        }
        return self.env.cr.mogrify("""ui.id IN %(model_ids)s""", where_values)

    def _number_cols(self, question):
        """
        For a given question, compute the number of columns it will create in the doc:
        * char_box, text_box, numerical_box, datetime, date: 1 column
        * simple_choice: 1 column, or 2 if comments allowed
        * multiple_choice:
            number of columns = number of choices + 1 if comments allowed
        * matrix:
           - if matrix_subtype = simple:
                 1 column per row + 1 extra column if comments allowed
           - if matrix_subtype = multiple:
                 number of rows * number of answers, + 1 if comments allowed
        """
        if question.question_type in SIMPLE_QUESTION_TYPES:
            return 1
        if question.question_type == "simple_choice":
            return 2 if question.comments_allowed else 1
        if question.question_type == "multiple_choice":
            number_answers = len(question.suggested_answer_ids)
            return number_answers + 1 if question.comments_allowed else number_answers
        if question.question_type == "matrix":
            number_rows = len(question.matrix_row_ids)
            if question.matrix_subtype == "simple":
                return number_rows + 1 if question.comments_allowed else number_rows
            if question.matrix_subtype == "multiple":
                number_col = number_rows * len(question.suggested_answer_ids)
                return number_col + 1 if question.comments_allowed else number_col

    def _compute_answer_simple_question_types(self, lines):
        """
        We always have to complete exactly 1 column.

        Possibilities:
        * len(lines) == 0: user input is in progress and no answer yet for this question
        * len(lines) == 1: this question has been answered or skipped.
        """
        answer = ""
        if len(lines) == 1:
            if lines.answer_type == "char_box":
                answer = lines.value_char_box
            elif lines.answer_type == "text_box":
                answer = lines.value_text_box
            elif lines.answer_type == "numerical_box":
                answer = lines.value_numerical_box
            elif lines.answer_type == "date":
                answer = lines.value_date
            elif lines.answer_type == "datetime":
                answer = lines.value_datetime
        return [answer]

    def _compute_answers_simple_choice(self, question, lines):
        """
        question: survey.question object, whose question_type is 'simple_choice'
        lines: all survey.user_input.line objects linked with this survey.user_input
          and with this question.

        Possibilities:
        * len(lines) == 0 : user input is in progress and no answer yet for this question
        * len(lines) == 1 : we have the answer for the question (it may be skipped or not)
        * len(lines) == 2 : comments were activated. We first have
          the answer (skipped or not) and then the comment
        """
        answer = ["" for i in range(self._number_cols(question))]
        if lines and not lines[0].skipped:
            answer[0] = lines[0].suggested_answer_id.value
        if len(lines) == 2:
            answer[1] = lines[1].value_char_box
        return answer

    def _compute_answers_multiple_choice(self, question, lines):
        """
        question: survey.question object, whose question_type is 'simple_choice'
        lines: all survey.user_input.line objects linked with this survey.user_input
          and with this question.

        Possibilities:
        * len(lines) == 0 : user input is in progress and no answer yet for this question
        * len(lines) > 0 and first line has skipped = True -> the whole question was skipped
        * len(lines) > 0 and last line is of char type -> a comment was given

        Otherwise all cases correspond to a suggested given answer.
        """
        answer = ["" for i in range(self._number_cols(question))]
        if not lines:
            return answer
        comment = ""
        if lines[-1].answer_type == "char_box":
            comment = lines[-1].value_char_box
            lines = lines[:-1]
            answer[-1] = comment
        if lines[0].skipped:
            return answer

        # Manage answers in right columns and don't forget to add the comment
        given_answers = {
            line.suggested_answer_id.id: line.suggested_answer_id.value
            for line in lines
        }
        all_answers = question.suggested_answer_ids.ids
        return [given_answers.get(a_id, "") for a_id in all_answers] + (
            [comment] if question.comments_allowed else []
        )

    def _compute_answers_simple_matrix(self, question, lines):
        """
        question: survey.question object, whose question_type is 'simple_choice'
        lines: all survey.user_input.line objects linked with this survey.user_input
          and with this question.

        Possibilities:
        * len(lines) == 0 : user input is in progress and no answer yet for this question
        * len(lines) > 0 and first line has skipped = True
          -> the whole matrix question was skipped
          NOTE: If some rows were skipped but not all,
          we only have the non skipped rows in lines
        * len(lines) > 0 and last line is of char type -> a comment was given
        """
        answer = ["" for i in range(self._number_cols(question))]
        if not lines:
            return answer
        comment = ""
        if lines[-1].answer_type == "char_box":
            comment = lines[-1].value_char_box
            lines = lines[:-1]
            answer[-1] = comment
        if lines[0].skipped:
            return answer

        # Manage each row and see if an answer is given
        answer = []
        given_rows_and_answers = {
            line.matrix_row_id.id: line.suggested_answer_id.value for line in lines
        }
        for row in question.matrix_row_ids:
            answer.append(given_rows_and_answers.get(row.id, ""))
        return answer if not question.comments_allowed else answer + [comment]

    def _compute_answers_multiple_matrix(self, question, lines):
        """
        question: survey.question object, whose question_type is 'simple_choice'
        lines: all survey.user_input.line objects linked with this survey.user_input
          and with this question.

        Possibilities:
        * len(lines) == 0 : user input is in progress and no answer yet for this question
        * len(lines) > 0 and first line has skipped = True
          -> the whole matrix question was skipped
          NOTE: If some rows were skipped but not all,
          we only have the non skipped rows in lines
        * len(lines) > 0 and last line is of char type -> a comment was given

        NOTE: We have one line per (row, suggested answer). So, for example, 3 answers to
        first row give 3 lines.
        """
        answer = ["" for i in range(self._number_cols(question))]
        if not lines:
            return answer
        comment = ""
        if lines[-1].answer_type == "char_box":
            comment = lines[-1].value_char_box
            lines = lines[:-1]
            answer[-1] = comment
        if lines[0].skipped:
            return answer

        # Manage each line and, as key, use (row_id, sugg_answer_id)
        answer = []
        given_rows_and_answers = {
            (
                line.matrix_row_id.id,
                line.suggested_answer_id.id,
            ): line.suggested_answer_id.value
            for line in lines
        }
        for row in question.matrix_row_ids:
            for sugg_answer in question.suggested_answer_ids:
                answer.append(given_rows_and_answers.get((row.id, sugg_answer.id), ""))
        return answer if not question.comments_allowed else answer + [comment]

    def _give_answers(self, user_input_id):
        """
        Returns a list of strings (answers).
        We take each question at one time, and we write the answers in the right column.
        """
        if not user_input_id:
            return False
        answers = []
        user_input = self.env["survey.user_input"].browse(user_input_id)

        for question in user_input.survey_id.question_ids:
            lines = user_input.user_input_line_ids.filtered(
                lambda line: line.question_id == question
            )
            if question.question_type in SIMPLE_QUESTION_TYPES:
                answers += self._compute_answer_simple_question_types(lines)
            elif question.question_type == "simple_choice":
                answers += self._compute_answers_simple_choice(question, lines)
            elif question.question_type == "multiple_choice":
                answers += self._compute_answers_multiple_choice(question, lines)
            elif (
                question.question_type == "matrix"
                and question.matrix_subtype == "simple"
            ):
                answers += self._compute_answers_simple_matrix(question, lines)
            elif (
                question.question_type == "matrix"
                and question.matrix_subtype == "multiple"
            ):
                answers += self._compute_answers_multiple_matrix(question, lines)

        return answers

    def _update_score(self, score):
        """
        If survey.scoring_type == 'no_scoring' -> score must be "" and not 0.
        """
        if self.survey_id.scoring_type == "no_scoring":
            return ""
        return score

    def _update_scoring_success(self, scoring_success):
        """
        If survey.scoring_type == 'no_scoring' -> scoring_success (string) must be ""
        """
        if self.survey_id.scoring_type == "no_scoring":
            return ""
        return scoring_success

    def _get_user_input_url(self, user_input_id):
        """
        Returns the Odoo URL to access the survey user input form view
        using the given id.
        """
        if not user_input_id:
            return ""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        custom_url = (
            "/web#id=%(user_input_id)d&action=%(action_id)d&active_id="
            "%(survey_id)d&model=survey.user_input&view_type=form&"
            "cids=&menu_id=%(menu_id)d"
            % {
                "user_input_id": user_input_id,
                "survey_id": self.survey_id.id,
                "action_id": self.env.ref("survey.action_survey_user_input").id,
                "menu_id": self.env.ref("survey.menu_surveys").id,
            }
        )
        return base_url + custom_url

    def _update_data(self, data, selections):
        """
        Update data and return export values

        NOTE: We select survey title here, to take the translated version

        :data: dict containing the data to format for export
        :selections: dict containing all possible values for some selection fields
        """
        data.update(
            {
                "object_type": "Survey",
                "object_name": self.survey_id.title,
                "interests": self._get_interests(),
                "answering_partner": self._compute_answering_partner(
                    data.get("number", "0"),
                    data.get("lastname", False),
                    data.get("firstname", False),
                ),
                "survey_status": selections.get("survey_states", {}).get(
                    data.get("survey_status"), data.get("survey_status")
                ),
                "membership_state": selections.get("membership_states", {}).get(
                    data.get("membership_state"), data.get("membership_state")
                ),
                "gender": selections.get("genders", {}).get(
                    data.get("gender"), data.get("gender")
                ),
                "answers": self._give_answers(data.get("user_input_id", False)),
                "score": self._update_score(data.get("score", 0)),
                "scoring_success": self._update_scoring_success(
                    data.get("scoring_success", False)
                ),
                "partner_url": self._get_partner_url(data.get("partner_id", False)),
                "user_input_url": self._get_user_input_url(
                    data.get("user_input_id", False)
                ),
            }
        )
        return data

    def _get_selections(self):
        """
        Build a dictionary with all membership states,
        all survey_states and all genders.
        """
        selections = super()._get_selections()
        selections_survey_ui = self.env["survey.user_input"].fields_get(
            allfields=["state"]
        )
        selections["survey_states"] = {
            k: v for k, v in selections_survey_ui["state"]["selection"]
        }
        return selections

    def _export(self, export_type):
        """
        Export the specified coordinates to a csv or xls file.
        :param export_type: str (csv or xls)
        """
        if not self.survey_id:
            return
        targets = self.env["survey.user_input"].search(
            [("survey_id", "=", self.survey_id.id)]
        )
        if export_type == "xls":
            content = self._get_xls(targets.ids)
        else:
            content = self._get_csv(targets.ids)
        content = base64.encodebytes(content)
        self.write(
            {
                "export_file": content,
                "export_filename": "extract." + export_type,
            }
        )

    def export(self):
        self._export(self.export_type)
        action = self.survey_id.export_action()
        action.update(
            {
                "res_id": self.id,
                "target": "new",
            }
        )
        return action
