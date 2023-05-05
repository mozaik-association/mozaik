# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast

from odoo import _, api, exceptions, fields, models, tools
from odoo.osv import expression


class DistributionListLine(models.Model):
    """
    Model used to represents lines of distribution list.
    These lines are used to include or exclude some recordset based
    on a domain.
    """

    _name = "distribution.list.line"
    _description = "Distribution List Line"

    distribution_list_line_tmpl_id = fields.Many2one(
        comodel_name="distribution.list.line.template",
        string="Distribution List Line Template",
        auto_join=True,
        required=True,
        index=True,
        ondelete="cascade",
    )
    distribution_list_id = fields.Many2one(
        comodel_name="distribution.list",
        string="Distribution List",
        required=True,
        index=True,
        ondelete="cascade",
        copy=False,
    )
    exclude = fields.Boolean(
        default=False,
        help="Check this box to exclude the filter result "
        "from the distribution list",
    )
    company_id = fields.Many2one(
        "res.company", "Company", related="distribution_list_id.company_id", store=True
    )
    trg_model = fields.Char(
        string="Target Model",
        related="distribution_list_id.dst_model_id.model",
        readonly=True,
    )
    bridge_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Bridge field",
        help="Bridge field between the source model (of the filter) "
        "and the target model (of the distribution list)",
        required=True,
        domain="["
        "('model_id', '=', src_model_id), "
        "('ttype', '=', 'many2one'), "
        "('relation', '=', trg_model), "
        "]",
        ondelete="cascade",
    )
    name = fields.Char(related="distribution_list_line_tmpl_id.name")
    domain = fields.Text(related="distribution_list_line_tmpl_id.domain",)
    src_model_id = fields.Many2one(
        related="distribution_list_line_tmpl_id.src_model_id"
    )
    src_model_model = fields.Char(
        related="distribution_list_line_tmpl_id.src_model_model"
    )

    def _get_valid_bridge_fields(self):
        """
        Get every fields available for each distribution.list.line
        :return: dict
        """
        src_models = self.mapped("src_model_id")
        dst_models = self.mapped("distribution_list_id.dst_model_id")
        domain = [
            ("ttype", "=", "many2one"),
            ("model_id", "in", src_models.ids),
            ("relation", "in", dst_models.mapped("model")),
        ]
        all_fields = self.env["ir.model.fields"].search(domain)

        domain = [
            ("ttype", "=", "integer"),
            ("name", "=", "id"),
            ("model_id", "in", src_models.ids),
        ]
        all_id_fields = self.env["ir.model.fields"].search(domain)

        results = {}
        for record in self:
            available_fields = all_fields.filtered(
                lambda f, r=record: f.model_id == r.src_model_id
                and f.relation == r.distribution_list_id.dst_model_id.model
            )
            if record.distribution_list_id.dst_model_id == record.src_model_id:
                available_fields |= all_id_fields.filtered(
                    lambda f, r=record: f.model_id == r.src_model_id
                )
            results.update({record: available_fields})
        return results

    @api.constrains(
        "bridge_field_id", "distribution_list_line_tmpl_id", "distribution_list_id"
    )
    def _constraint_valid_bridge_field_id(self):
        """
        Constrain to check if the bridge_field_id set is correct
        :return:
        """
        fields_available = self._get_valid_bridge_fields()
        # Available fields
        bad_dist_list_lines = self.filtered(
            lambda l: l.bridge_field_id not in fields_available.get(l)
        )
        if bad_dist_list_lines:
            details = "\n- ".join(bad_dist_list_lines.mapped("name"))
            message = (
                _(
                    "These filters are not valid because the bridge field "
                    "is not related to the target model of "
                    "the distribution list!\n- %s"
                )
                % details
            )
            raise exceptions.ValidationError(message)

    def _get_eval_domain(self):
        """
        Eval the domain
        Note: copy paste of the same Odoo function on ir.filters
        :return: list
        """
        self.ensure_one()
        return ast.literal_eval(self.domain)

    @api.onchange("src_model_id", "distribution_list_id")
    def _onchange_src_model_id(self):
        self.ensure_one()
        fields_available = self._get_valid_bridge_fields().get(self)
        if len(fields_available) == 1:
            self.bridge_field_id = fields_available
        else:
            self.bridge_field_id = fields_available.filtered(lambda s: s.name == "id")

    # pylint: disable=E8103
    def _get_target_recordset(self):
        """
        Get target recordset where the related domain is applied with a OR
        between every domains
        :return: target recordset
        """
        # All current recordset should belong to the same model
        if not self:
            return False
        # The target model of every lines should be the same
        self.mapped("distribution_list_id").ensure_one()
        target_model = self.mapped("distribution_list_id.dst_model_id").model
        targets = self.env[target_model].browse()
        for bridge_field in self.mapped("bridge_field_id"):
            self_model = self.filtered(
                lambda r, bf=bridge_field: r.bridge_field_id == bf
            )
            domains = [r._get_eval_domain() for r in self_model]
            big_domain = []
            if domains != [[]]:
                big_domain = expression.OR(domains)
            source_model = bridge_field.model_id.model
            field_name = bridge_field.name
            try:
                self.flush()
                if field_name == "self":
                    field_name = "id"
                # not the best, but use directly the sql to improve perf
                # without that, it will need 2 call, one search, one read
                self.env[source_model].check_access_rights("read")
                query = self.env[source_model]._where_calc(big_domain)
                self.env[source_model]._apply_ir_rules(query, "read")
                from_clause, where_clause, where_clause_params = query.get_sql()
                query_str = 'SELECT "%s".%s FROM %s WHERE %s' % (
                    self.env[source_model]._table,
                    field_name,
                    from_clause,
                    where_clause,
                )
                self.env.cr.execute(query_str, where_clause_params)
                ids = [r[0] for r in self.env.cr.fetchall()]
                targets |= self.env[target_model].browse(ids)
            except Exception as e:
                message = _(
                    "A filter for the target model %s is not valid.\n" "Details: %s"
                ) % (target_model, tools.ustr(e))
                raise exceptions.UserError(message) from e
        return targets

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

    def action_redefine_domain(self):
        pass
