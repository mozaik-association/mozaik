# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import csv
from io import StringIO

from psycopg2.extensions import AsIs

from odoo import _, api, exceptions, fields, models


class ExportCsv(models.TransientModel):
    _name = "export.csv"
    _description = "Export CSV Wizard"

    export_file = fields.Binary(
        string="CSV",
        readonly=True,
    )
    export_filename = fields.Char(
        string="Export CSV filename",
    )

    @api.model
    def _get_select(self):
        return """SELECT
                 p.identifier,
                 p.name,
                 p.lastname,
                 p.firstname,
                 p.usual_lastname,
                 p.usual_firstname,
                 p.birthdate_date,
                 p.gender,
                 p.lang,
                 p.title,
                 p.technical_name,
                 CASE
                    WHEN cc.line IS NOT NULL
                    THEN cc.line
                    ELSE p.printable_name
                 END AS printable_name,
                 cc.id as co_residency_id,
                 cc.line2 as co_residency,
                 p.membership_state_id as state_id,
                 address.street2 as street2,
                 address.street as street,
                 address.zip as final_zip,
                 address.city as city,
                 country.id as country_id,
                 country.name as country_name,
                 country.code as country_code,
                 p.phone as fix,
                 p.mobile as mobile,
                 p.email"""

    @api.model
    def _common_joins(self):
        return """

                LEFT OUTER JOIN address_address address
                ON address.id = p.address_address_id

                LEFT OUTER JOIN res_country country
                ON country.id = address.country_id

                LEFT OUTER JOIN co_residency cc
                ON cc.id = p.co_residency_id"""

    @api.model
    def _from_virtual_target(self):
        query = """FROM virtual_target vt

                JOIN res_partner p
                 ON p.id = vt.partner_id

                %(common_join)s"""
        return query

    @api.model
    def _from_partner(self):
        query = """FROM res_partner p

                %(common_join)s"""
        return query

    @api.model
    def _get_csv_rows(self):
        """
        Get the rows (header) for the specified model.
        :return: list of str
        """
        header = [
            _("Number"),
            _("Name"),
            _("Lastname"),
            _("Firstname"),
            _("Usual Lastname"),
            _("Usual Firstname"),
            _("Co-residency Line 1"),
            _("Co-residency Line 2"),
            _("State"),
            _("Birth Date"),
            _("Gender"),
            _("Language"),
            _("Title"),
            _("Street2"),
            _("Street"),
            _("Zip"),
            _("City"),
            _("Country Code"),
            _("Country"),
            _("Phone"),
            _("Mobile"),
            _("Email"),
        ]
        return header

    @api.model
    def _get_order_by(self, order_by):
        """
        Based on the given order_by, build the order by
        :param order_by: str
        :return: str
        """
        r_order_by = "p.id"
        if order_by in ["identifier", "technical_name"]:
            r_order_by = "p.%s" % order_by
        elif order_by:
            r_order_by = "country_name, final_zip, p.technical_name"
        return r_order_by

    @api.model
    def _get_csv_values(self, values):
        """
        Get the values of the specified obj taking into account the VIP
        obfuscation principle
        :param values: dict
        :param obfuscation: str
        :return: list of str
        """
        keys = [
            "identifier",
            "name",
            "lastname",
            "firstname",
            "usual_lastname",
            "usual_firstname",
            "printable_name",
            "co_residency",
            "state",
            "birthdate_date",
            "gender",
            "lang",
            "title",
            "street2",
            "street",
            "final_zip",
            "city",
            "country_code",
            "country_name",
            "fix",
            "mobile",
            "email",
        ]
        export_values = [values.get(k, "*****") for k in keys]
        return export_values

    @api.model
    def _prefetch_csv_datas(self, model, model_ids):
        """
        Build the SQL query and load data to build CSV
        :param model: str
        :param model_ids: list of int
        :return: list of dict
        """
        if not model_ids:
            return
        where_query = "%(table_join)s.id IN %(model_ids)s"
        if model == "virtual.target":
            table_join = "vt"
            from_sql = self._from_virtual_target()
        elif model == "res.partner":
            table_join = "p"
            from_sql = self._from_partner()
        else:
            raise exceptions.UserError(
                _("Model %s not supported for csv export!") % model
            )
        where_values = {
            "table_join": AsIs(table_join),
            "model_ids": tuple(model_ids),
        }
        where_query = self.env.cr.mogrify(where_query, where_values)
        select = self._get_select()
        from_values = {
            "common_join": AsIs(self._common_joins()),
        }
        from_sql = self.env.cr.mogrify(from_sql, from_values)
        order_by = self._get_order_by(self.env.context.get("sort_by"))
        query = "%(select)s %(from)s WHERE %(where_query)s " "ORDER BY %(order_by)s"
        values = {
            "where_query": AsIs(where_query.decode()),
            "order_by": AsIs(order_by),
            "select": AsIs(select),
            "from": AsIs(from_sql.decode()),
        }
        self.env.cr.execute(query, values)
        for row in self.env.cr.dictfetchall():
            yield row

    @api.model
    def _get_csv(self, model, model_ids, group_by=False):
        """
        Build a CSV file related to a coordinate model related to model_ids
        :param model: str
        :param model_ids: list of int
        :param group_by: str
        :return: str
        """
        if not model or not model_ids:
            return ""
        states = self.env["membership.state"].search([])
        states = {st.id: st.name for st in states}
        titles = self.env["res.partner.title"].search([])
        titles = {title.id: title.name for title in titles}
        countries = self.env["res.country"].search([])
        countries = {cnt.id: cnt.name for cnt in countries}
        selections = self.env["res.partner"].fields_get(allfields=["gender", "lang"])
        genders = {k: v for k, v in selections["gender"]["selection"]}
        langs = {k: v for k, v in selections["lang"]["selection"]}
        headers = self._get_csv_rows()
        with StringIO() as memory_file:
            writer = csv.writer(memory_file)
            writer.writerow(headers)
            for data in self._prefetch_csv_datas(model, model_ids):
                # Update data depending on others models
                data.update(
                    {
                        "state": states.get(data.get("state_id"), data.get("state")),
                        "title": titles.get(data.get("title"), ""),
                        "country_name": countries.get(
                            data.get("country_id"), data.get("country_name")
                        ),
                        "gender": genders.get(data.get("gender"), data.get("gender")),
                        "lang": langs.get(data.get("lang"), data.get("lang")),
                    }
                )
                if not data.get("co_residency_id") and data.get("title"):
                    data["printable_name"] = "%s %s" % (
                        data["title"],
                        data["printable_name"],
                    )
                export_values = self._get_csv_values(data)
                writer.writerow(export_values)
            csv_content = memory_file.getvalue()
        return csv_content

    def export(self):
        self.ensure_one()
        context = self.env.context
        model = context.get("active_model")
        model_ids = context.get("active_ids", context.get("active_id", []))
        csv_content = self._get_csv(model, model_ids)
        self.write(
            {
                "export_file": base64.b64encode(csv_content.encode("utf-8")),
                "export_filename": _("Extract") + ".csv",
            }
        )
        action = self.env.ref("mozaik_communication.export_csv_postal_action").read()[0]
        action.update(
            {
                "res_id": self.id,
                "target": "new",
            }
        )
        return action
