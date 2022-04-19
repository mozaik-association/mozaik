# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
from io import StringIO

from psycopg2.extensions import AsIs

from odoo import _, api, fields, models

SIMPLE_QUESTION_TYPES = ["text_box", "char_box", "numerical_box", "date", "datetime"]


class SurveyExportCsv(models.TransientModel):

    _name = "survey.export.csv"
    _description = "Survey export CSV"

    survey_id = fields.Many2one(
        comodel_name="survey.survey",
    )
    export_file = fields.Binary(
        string="CSV",
        readonly=True,
    )
    export_filename = fields.Char(
        string="Export CSV filename",
    )

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

    def _get_csv_rows(self):
        """
        Get the columns (header) for survey answers
        :return: list of str
        """
        header = [
            _("Object Type"),
            _("Object Name"),
            _("Interests"),
            _("Answering Partner"),
            _("Partner ID"),
            # _("Partner form URL"),
            # _("Token ID"),
            # _("Survey answer URL"),
            # _("Answering datetime"),
            # _("Modification datetime"),
            _("Status"),
            _("Lastname"),
            _("Firstname"),
            # _("Gender"),
            # _("Birth Date"),
            # _("Membership State"),
            # _("Email"),
            # _("Mobile"),
            # _("Street"),
            # _("Street2"),
            # _("Zip"),
            # _("City"),
            # _("Score"),
            # _("Quiz passed"),
        ]
        self._add_questions_to_cols(header)
        return header

    @api.model
    def _get_csv_values(self, values):
        """
        Get the values of the specified object
        :param values: dict
        :return: list of str that corresponds to a row of the file
        """
        keys = [
            "object_type",
            "object_name",
            "interests",
            "answering_partner",
            "partner_id",
            "survey_status",
            "lastname",
            "firstname",
        ]
        export_values = [values.get(k, "") for k in keys]
        export_values += values.get("answers", [])
        return export_values

    def _compute_answering_partner(self, number, lastname, firstname):
        """
        From number, firstname and lastname, returns "Number - Lastname Firstname"
        or just "Lastname Firstname" if no number is given
        """
        return (
            (str(number) + " - " if number else "")
            + str(lastname or "")
            + " "
            + str(firstname or "")
        )

    def _get_select(self):
        """
        Return select part of the query
        """
        return """
        SELECT
        s.title as object_name,
        p.lastname,
        p.firstname,
        p.identifier as number,
        p.id as partner_id,
        ui.id as user_input_id,
        ui.state as survey_status
        """

    def _get_from(self):
        """
        Return from part of the query
        """
        return """
        FROM survey_user_input ui
        LEFT JOIN res_partner p ON ui.partner_id = p.id
        JOIN survey_survey s ON s.id = ui.survey_id
        """

    def _get_where(self, model_ids):
        """
        Return where part of the query
        """
        where_values = {
            "model_ids": tuple(model_ids),
        }
        return self.env.cr.mogrify("""ui.id IN %(model_ids)s""", where_values)

    @api.model
    def _prefetch_csv_datas(self, model_ids):
        """
        Build the SQL query and load data to build CSV
        :param model_ids: list of int
        :return: list of dict
        """
        if not model_ids:
            return
        where_query = self._get_where(model_ids)
        select = self._get_select()
        from_sql = self._get_from()
        query = "%(select)s %(from)s WHERE %(where_query)s "
        values = {
            "where_query": AsIs(where_query.decode()),
            "select": AsIs(select),
            "from": AsIs(from_sql),
        }
        self.env.cr.execute(query, values)
        for row in self.env.cr.dictfetchall():
            yield row

    def _number_cols(self, question):
        """
        For a given question, compute the number of columns it will create in the CSV:
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
                lambda l: l.question_id == question
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

    @api.model
    def _get_csv(self, model_ids):
        """
        Build a CSV file related to a coordinate model related to model_ids
        :param model_ids: list of int
        :return: str
        """
        if not model_ids:
            return ""
        states = self.env["membership.state"].search([])
        states = {st.id: st.name for st in states}
        selections = self.env["res.partner"].fields_get(allfields=["gender", "lang"])
        genders = {k: v for k, v in selections["gender"]["selection"]}
        headers = self._get_csv_rows()

        with StringIO() as memory_file:
            writer = csv.writer(memory_file)
            writer.writerow(headers)
            for data in self._prefetch_csv_datas(model_ids):
                # Update data depending on others models
                data.update(
                    {
                        "object_type": "Survey",
                        "answering_partner": self._compute_answering_partner(
                            data.get("number", "0"),
                            data.get("lastname", False),
                            data.get("firstname", False),
                        ),
                        "state": states.get(data.get("state_id"), data.get("state")),
                        "gender": genders.get(data.get("gender"), data.get("gender")),
                        "answers": self._give_answers(data.get("user_input_id", False)),
                    }
                )
                export_values = self._get_csv_values(data)
                writer.writerow(export_values)
            csv_content = memory_file.getvalue()
        return csv_content

    def export_csv(self):
        """
        Export the specified coordinates to a CSV file.
        :param model: str
        :param group_by: bool
        :return: bool
        """
        if not self.survey_id:
            return
        targets = self.env["survey.user_input"].search(
            [("survey_id", "=", self.survey_id.id)]
        )
        csv_content = self._get_csv(targets.ids)
        csv_content = base64.encodebytes(csv_content.encode())
        self.write(
            {
                "export_file": csv_content,
                "export_filename": "extract.csv",
            }
        )

    def export(self):
        self.export_csv()
        action = self.survey_id.export_csv_action()
        action.update(
            {
                "res_id": self.id,
                "target": "new",
            }
        )
        return action
