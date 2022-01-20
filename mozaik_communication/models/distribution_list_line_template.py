# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.osv import expression


class DistributionListLineTemplate(models.Model):
    _name = "distribution.list.line.template"
    _inherit = ["mozaik.abstract.model", "distribution.list.line.template"]
    _unicity_keys = "N/A"

    name = fields.Char(tracking=True)
    domain = fields.Text(tracking=True)
    src_model_id = fields.Many2one(tracking=True)

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
        result.update({"domain": domain})
        return result
