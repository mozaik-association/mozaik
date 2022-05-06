# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import _, models
from odoo.osv import expression


class DistributionListLine(models.Model):
    _name = "distribution.list.line"
    _inherit = [
        "mozaik.abstract.model",
        "distribution.list.line",
    ]
    _unicity_keys = "N/A"

    def _get_target_recordset(self):
        """
        For excluding filters the result is transformed
        to exclude all target records linked
        to the concerned partners
        :return: target recordset
        """
        results = super()._get_target_recordset()
        partner_path = self.mapped("distribution_list_id").partner_path
        if results and all(self.mapped("exclude")) and partner_path:
            query = (
                "SELECT id from %(table)s "
                "WHERE %(partner_path)s in ("
                "   SELECT %(partner_path)s FROM %(table)s WHERE id in %(ids)s)"
            )
            self.env.cr.execute(
                query,
                {
                    "table": AsIs(results._table),
                    "partner_path": AsIs(partner_path),
                    "ids": tuple(results.ids),
                },
            )

            ids = [r[0] for r in self.env.cr.fetchall()]
            if ids:
                # apply security
                results = results.search([("id", "in", ids)])
        return results

    def action_show_filter_result_without_coordinate(self):
        """
        Show the result of the list without coordinate
        :return: dict/action
        """
        self.ensure_one()
        result = self.action_show_filter_result()
        result.update({"name": _("Result of %s without coordinate") % self.name})
        domain = result.get("domain", [])
        domain = expression.AND([domain, [("active", "=", False)]])
        result.update(
            {
                "domain": domain,
            }
        )
        return result
