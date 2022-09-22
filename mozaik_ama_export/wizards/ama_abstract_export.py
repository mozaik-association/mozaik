# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import datetime
from io import BytesIO, StringIO

import xlsxwriter
from psycopg2.extensions import AsIs

from odoo import _, api, models


class AmaAbstractExport(models.TransientModel):

    _name = "ama.abstract.export"
    _description = "Ama Abstract Export"

    def _get_selections(self):
        """
        Return a dictionary for which keys are selection field names, and values
        are dictionaries containing all selection values.

        Add res.partner values: membership states and genders.
        Intended to be extended
        """
        selections = {}
        membership_states = self.env["membership.state"].search([])
        selections["membership_states"] = {st.id: st.name for st in membership_states}
        selections_partner = self.env["res.partner"].fields_get(allfields=["gender"])
        selections["genders"] = {
            k: v for k, v in selections_partner["gender"]["selection"]
        }

        return selections

    def _get_headers(self):
        """
        Get the columns (header)
        :return: list of str

        Intended to be extended
        """
        return []

    def _get_xls_formats(self, workbook):
        """
        Define workbook formats
        """
        return {
            "format_date": workbook.add_format({"num_format": "dd/mm/yyyy"}),
            "format_datetime": workbook.add_format(
                {"num_format": "dd/mm/yyyy hh:mm:ss"}
            ),
        }

    def _xls_writerow(self, worksheet, row_number, row, formats):
        """
        :row_number: row number of the xls file
        :row: list of values to write in a row
        :formats: dict of formats to use
        """
        col = 0
        for elem in row:
            if isinstance(elem, datetime.datetime):
                worksheet.write(row_number, col, elem, formats["format_datetime"])
            elif isinstance(elem, datetime.date):
                worksheet.write(row_number, col, elem, formats["format_date"])
            else:
                if isinstance(elem, bool):
                    worksheet.write(row_number, col, _("True") if elem else _("False"))
                else:
                    worksheet.write(row_number, col, elem)
            col += 1

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

    def _get_partner_url(self, partner_id):
        """
        Returns the Odoo URL to access the partner form view of the
        partner given by its id.
        """
        if not partner_id:
            return ""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        custom_url = (
            "/web#id=%(partner_id)d&action=%(action_id)d&"
            "model=res.partner&view_type=form&cids=&menu_id=%(menu_id)d"
            % {
                "partner_id": partner_id,
                "action_id": self.env.ref(
                    "mozaik_person.res_partner_natural_person_action"
                ).id,
                "menu_id": self.env.ref("contacts.menu_contacts").id,
            }
        )
        return base_url + custom_url

    def _get_select(self):
        """
        Return select part of the query

        Will be overwritten
        """
        return ""

    def _get_from(self):
        """
        Return from part of the query

        Will be overwritten
        """
        return ""

    def _where_select(self):
        """
        Return where part of the query

        Will be overwritten
        """
        return ""

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

    def _get_row_values(self, values):
        """
        Get the values of the specified object
        :param values: dict
        :return: list of str that corresponds to a row of the file

        Intended to be extended
        """
        return []

    def _update_data(self, data, selections):
        """
        Update data

        Intended to be extended
        """
        return data

    def _update_and_format_data(self, data, selections):
        """
        Update data and return export values

        :data: dict containing the data to format for export
        :selections: dict containing all possible values for some selection fields
        :return: a list of strings corresponding to the data of a row
        """
        data = self._update_data(data, selections)
        return self._get_row_values(data)

    def _get_xls(self, model_ids):
        """
        Build a xls file related to a coordinate model related to model_ids
        :param model_ids: list of int
        :return: str
        """
        if not model_ids:
            return ""

        selections = self._get_selections()
        headers = self._get_headers()

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        writer = workbook.add_worksheet("Sheet 1")
        formats = self._get_xls_formats(workbook)
        self._xls_writerow(writer, 0, headers, formats)
        row_number = 1
        for data in self._prefetch_csv_datas(model_ids):
            export_values = self._update_and_format_data(data, selections)
            self._xls_writerow(writer, row_number, export_values, formats)
            row_number += 1
        workbook.close()
        xls_content = output.getvalue()

        return xls_content

    def _get_csv(self, model_ids):
        """
        Build a CSV file related to a coordinate model related to model_ids
        :param model_ids: list of int
        :return: str
        """
        if not model_ids:
            return ""
        selections = self._get_selections()
        headers = self._get_headers()

        with StringIO() as memory_file:
            writer = csv.writer(memory_file)
            writer.writerow(headers)
            for data in self._prefetch_csv_datas(model_ids):
                export_values = self._update_and_format_data(data, selections)
                writer.writerow(export_values)
            csv_content = memory_file.getvalue()
        return csv_content.encode()
