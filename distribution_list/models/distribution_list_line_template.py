# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast

from odoo import _, api, fields, models


class DistributionListLineTemplate(models.Model):

    _name = "distribution.list.line.template"
    _description = "Distribution List Line Template"
    _order = "name"

    name = fields.Char(required=True)
    domain = fields.Text("Expression", required=True, default="[]")
    src_model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        index=True,
        default=lambda self: self._get_default_src_model_id(),
        domain=lambda self: self._get_domain_src_model_id(),
        ondelete="cascade",
    )
    src_model_model = fields.Char(
        string="Model name", related="src_model_id.model", readonly=True
    )
    included_distribution_list_line_ids = fields.One2many(
        comodel_name="distribution.list.line",
        inverse_name="distribution_list_line_tmpl_id",
        string="Included Distribution List Lines",
        domain=[("exclude", "!=", True)],
    )
    excluded_distribution_list_line_ids = fields.One2many(
        comodel_name="distribution.list.line",
        inverse_name="distribution_list_line_tmpl_id",
        string="Excluded Distribution List Lines",
        domain=[("exclude", "=", True)],
    )

    _sql_constraints = [
        (
            "unique_name_dist_list_line_tmpl",
            "unique(name)",
            "The name of a filter must be unique. A filter with the same name "
            "already exists.",
        ),
    ]

    @api.onchange("src_model_id")
    def _onchange_src_model_id(self):
        self.ensure_one()
        self.domain = "[]"

    def write(self, vals):
        """
        If `src_model_id` is changed and not `domain`, reset domain to its
        default value: `[]`
        :param vals: dict
        :return: bool
        """
        if vals.get("src_model_id") and not vals.get("domain"):
            vals.update({"domain": "[]"})
        return super().write(vals)

    @api.model
    def _get_src_model_names(self):
        """
        Get the list of available model name
        Intended to be inherited
        :return: list of string
        """
        return []

    @api.model
    def _get_domain_src_model_id(self):
        """
        Get domain of available models
        :return: list of tuple (domain)
        """
        mods = self._get_src_model_names() or ["res.partner"]
        return [("model", "in", mods)]

    @api.model
    def _get_default_src_model_id(self):
        """
        Get the default src model
        :return: model recordset
        """
        model = False
        mods = self._get_src_model_names() or ["res.partner"]
        if len(mods) == 1:
            model = self.env["ir.model"].search([("model", "in", mods)])
            model = model or self.env.ref("base.model_res_partner")
        return model

    def _get_eval_domain(self):
        """
        Eval the domain
        Note: copy paste of the same Odoo function on ir.filters
        :return: list
        """
        self.ensure_one()
        return ast.literal_eval(self.domain)

    def action_show_filter_result(self):
        """
        Show the result of the filter
        :return: dict/action
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Result of %s") % self.name,
            "view_mode": "tree",
            "res_model": self.src_model_id.model,
            "context": self.env.context,
            "domain": self._get_eval_domain(),
            "target": "current",
        }
