# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast
from odoo import api, models, exceptions, tools, fields, _
from odoo.fields import first
from odoo.osv import expression


class DistributionListLine(models.Model):
    """
    Model used to represents lines of distribution list.
    These lines are used to include or exclude some recordset based
    on a domain.
    """
    _name = 'distribution.list.line'
    _description = 'Distribution List Line'

    name = fields.Char(
        required=True,
    )
    distribution_list_id = fields.Many2one(
        "distribution.list",
        "Distribution list",
        required=True,
        index=True,
    )
    exclude = fields.Boolean(
        help="Check this box to exclude the result of this filter/line on "
             "the related distribution list",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        related="distribution_list_id.company_id",
        store=True,
    )
    domain = fields.Text(
        "Expression",
        required=True,
        default="[]",
    )
    src_model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        index=True,
        default=lambda self: self.env.ref("base.model_res_partner").id,
    )
    bridge_field_id = fields.Many2one(
        "ir.model.fields",
        "Bridge field",
        help="Bridge field between the source model (of this line/filter) "
             "and the destination model (on the distribution list. If the "
             "model is the same, let it empty",
        required=True,
    )
    _sql_constraints = [
        ('unique_name_by_dist_list', 'unique(name, distribution_list_id)',
         'The name of a filter must be unique. A filter with the same name '
         'already exists.'),
    ]

    @api.multi
    def _get_valid_bridge_field_id(self):
        """
        Get every fields available for each distribution.list.line
        :return: dict
        """
        src_models = self.mapped("src_model_id")
        dst_models = self.mapped("distribution_list_id.dst_model_id")
        domain = [
            ('ttype', '=', 'many2one'),
            ('model_id', 'in', src_models.ids),
            ('relation', 'in', dst_models.mapped("model")),
        ]
        all_fields = self.env['ir.model.fields'].search(domain)

        domain = [
            ('ttype', '=', 'integer'),
            ('name', '=', 'id'),
            ('model_id', 'in', src_models.ids),
        ]
        all_id_fields = self.env['ir.model.fields'].search(domain)

        results = {}
        for record in self:
            available_fields = all_fields.filtered(
                lambda f, r=record: f.model_id.id == r.src_model_id.id and
                f.relation == r.distribution_list_id.dst_model_id.model)
            if record.distribution_list_id.dst_model_id.id == \
                    record.src_model_id.id:
                available_fields |= all_id_fields.filtered(
                    lambda f, r=record: f.model_id.id == r.src_model_id.id)
            results.update({
                record: available_fields,
            })
        return results

    @api.multi
    @api.constrains('bridge_field_id', 'src_model_id', 'distribution_list_id')
    def _constraint_valid_bridge_field_id(self):
        """
        Constrain to check if the bridge_field_id set is correct
        :return:
        """
        fields_available = self._get_valid_bridge_field_id()
        # Available fields
        bad_dist_list_lines = self.filtered(
            lambda l: l.bridge_field_id.id not in fields_available.get(l).ids)
        if bad_dist_list_lines:
            details = "\n- ".join(bad_dist_list_lines.mapped("name"))
            message = _("These distribution list lines are not valid because "
                        "the bridge field is not related to the destination "
                        "model set on the distribution list!"
                        "\n- %s") % details
            raise exceptions.ValidationError(message)

    @api.multi
    def _get_eval_domain(self):
        """
        Eval the domain
        Note: copy paste of the same Odoo function on ir.filters
        :return: list
        """
        self.ensure_one()
        return ast.literal_eval(self.domain)

    @api.onchange('src_model_id', 'distribution_list_id')
    def _onchange_src_model_id(self):
        self.domain = self._fields.get('src_model_id').default(self)
        fields_available = self._get_valid_bridge_field_id().get(self)
        if len(fields_available) == 1:
            self.bridge_field_id = fields_available
        result = {
            'domain': {
                'bridge_field_id': [('id', 'in', fields_available.ids)],
            },
        }
        return result

    @api.multi
    def copy(self, default=None):
        """
        When copying then add '(copy)' at the end of the name
        :param default: None or dict
        :return: self recordset
        """
        self.ensure_one()
        default = default or {}
        if 'name' not in default:
            default.update({
                'name': _('%s (copy)') % self.name,
            })
        result = super(DistributionListLine, self).copy(default=default)
        return result

    def _save_domain(self, domain):
        """
        This method will update `domain`
        :param domain: str
        :return:
        """
        self.write({
            "domain": domain,
        })

    @api.model
    def create(self, vals):
        """

        :param vals: dict
        :return: self recordset
        """
        if not vals.get('domain'):
            vals.update({
                'domain': str(self._fields.get('domain').default(self)),
            })
        return super(DistributionListLine, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        If `src_model_id` is changed and not `domain`, reset domain to its
        default value: `[]`
        :param vals: dict
        :return: bool
        """
        if vals.get('src_model_id') and not vals.get('domain'):
            vals.update({
                'domain': self._fields.get('domain').default(self),
            })
        return super(DistributionListLine, self).write(vals)

    @api.multi
    def _get_target_recordset(self):
        """
        Get target recordset where the related domain is applied with a AND
        between every domains
        :return: target recordset
        """
        # All current recordset should belong to the same model
        if not self:
            return False
        # The target model of every lines should be the same
        target_model = first(self).distribution_list_id.dst_model_id.model
        targets = self.env[target_model].browse()
        for target_model in self.mapped("src_model_id.model"):
            self_model = self.filtered(
                lambda r: r.bridge_field_id.model_id.model == target_model)
            domains = [r._get_eval_domain() for r in self_model]
            big_domain = expression.OR(domains)
            try:
                results = self.env[target_model].search(big_domain)
                for field_name in self_model.mapped("bridge_field_id.name"):
                    if field_name == 'id':
                        targets |= results
                    else:
                        targets |= results.mapped(field_name)
            except Exception as e:
                message = _("A filter for the target model %s is not valid.\n"
                            "Details: %s") % (target_model, tools.ustr(e))
                raise exceptions.UserError(message)
        return targets

    @api.multi
    def get_list_from_domain(self):
        """
        This method will provide a 'test' by returning a dictionary
        that allow user to see the result of the domain expression applied on
        the selected model
        :return: dict/action
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Result of %s') % self.name,
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': self.src_model_id.model,
            'view_id': False,
            'views': [(False, 'tree')],
            'context': self.env.context.copy(),
            'domain': self.domain,
            'target': 'current',
        }

    @api.multi
    def action_partner_selection(self):
        """
        Launch an action act_windows with special parameters:
           * view_mode      --> tree_partner_selection
               View Customized With JavaScript and QWeb

           * flags          --> search_view
               Put the search_view to true allow to show
               The SearchBox into a PopUp window
        :return:
        """
        self.ensure_one()
        context = self.env.context.copy()
        context.update({
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': '%s List' % self.src_model_id.name,
            'res_model': self.src_model_id.model,
            'view_mode': 'tree',
            'target': 'new',
            'flags': {'search_view': True},
            'context': context,
        }
