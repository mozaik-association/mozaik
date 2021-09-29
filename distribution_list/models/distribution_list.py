# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, exceptions, fields, _
from odoo.osv import expression


class DistributionList(models.Model):

    _name = 'distribution.list'
    _description = 'Distribution List'
    _order = 'name'

    name = fields.Char(
        required=True,
    )
    to_include_distribution_list_line_ids = fields.One2many(
        "distribution.list.line",
        "distribution_list_id",
        "Filters to Include",
        domain=[('exclude', '!=', True)],
        copy=True,
    )
    to_exclude_distribution_list_line_ids = fields.One2many(
        "distribution.list.line",
        "distribution_list_id",
        "Filters to Exclude",
        domain=[('exclude', '=', True)],
        copy=True,
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
    )
    dst_model_id = fields.Many2one(
        "ir.model",
        string="Target Model",
        required=True,
        default=lambda self: self._get_default_dst_model_id(),
        domain=lambda self: self._get_domain_dst_model_id(),
        ondelete='cascade',
    )
    note = fields.Text(
    )

    _sql_constraints = [
        ('constraint_uniq_name', 'unique(company_id, name)',
         "This name already exists for this company"),
    ]

    @api.model
    def _get_dst_model_names(self):
        """
        Get the list of available model name
        Intended to be inherited
        :return: list of string
        """
        return []

    @api.model
    def _get_domain_dst_model_id(self):
        """
        Get domain of available models
        :return: list of tuple (domain)
        """
        mods = self._get_dst_model_names() or ['res.partner']
        return [('model', 'in', mods)]

    @api.model
    def _get_default_dst_model_id(self):
        """
        Get the default dst model
        :return: model recordset
        """
        model = False
        mods = self._get_dst_model_names() or ['res.partner']
        if len(mods) == 1:
            model = self.env['ir.model'].search([('model', 'in', mods)])
            model = model or self.env.ref('base.model_res_partner')
        return model

    def _get_target_if_no_included_filter(self):
        self.ensure_one()
        target_model = self.dst_model_id.model
        return self.env[target_model].browse()

    def copy(self, default=None):
        """
        Copy the name (with a 'copy' after) and also copy include/exclude
        related lines
        :param default: None or dict
        :return: self recordset
        """
        self.ensure_one()
        default = default or {}
        default.update({
            'name': _("%s (copy)") % self.name,
        })
        result = super(DistributionList, self).copy(default=default)
        return result

    def mass_mailing(self):
        """
        Get mass mailing wizard (using action) related to current list.
        :return: dict (action)
        """
        self.ensure_one()
        context = self.env.context.copy()
        email_template = self.env.ref(
            "distribution_list.mail_template_partner_distribution_list")
        context.update({
            'default_composition_mode': 'mass_mail',
            'default_partner_to': '${object.id}',
            'active_model': self.dst_model_id.model,
            'default_distribution_list_id': self.id,
            'default_res_id': 0,
            'default_template_id': email_template.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Mass Mailing'),
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'mail.compose.message',
            'context': context,
        }

    def _get_target_from_distribution_list(self):
        """
        Computes records matching the entire distribution list
        depending on filters to include or exclude.
        :return: target recordset
        """
        self.ensure_one()
        include_dll = self.to_include_distribution_list_line_ids
        exclude_dll = self.to_exclude_distribution_list_line_ids
        if not include_dll:
            # without filter to include get records
            # from a method to override
            results_include = self._get_target_if_no_included_filter()
        else:
            # get records to include
            results_include = include_dll._get_target_recordset()

        # get records to exclude
        if exclude_dll:
            results_exclude = exclude_dll._get_target_recordset()
        else:
            results_exclude = self.env[self.dst_model_id.model].browse()

        results = results_include - results_exclude
        return results

    @api.model
    def _get_target(
            self, source_records, bridge_field, domain, target_model, sort):
        """
        From an initial list of ids of a model, returns a list
        containing the value of a specific field of this model
        optionally filtered by an extra domain and/or
        ordered by a given sort criteria
        Final result is a list of unique values (sorted or not)
        If a target_model is provided, security is applied
        :param source_records: recordset
        :param bridge_field: str
        :param domain: list
        :param sort: str
        :return: recordset
        """
        source_model = source_records._name
        results = self.env[target_model or source_model].browse()
        if not bridge_field:
            pass
        elif not source_records._fields.get(bridge_field):
            raise exceptions.UserError(
                _("The target model %s doesn't have a field named "
                  "%s") % (source_model, bridge_field))
        elif source_records:
            domain = domain or []
            domain = expression.AND([
                domain,
                [
                    ('id', 'in', source_records.ids),
                ],
            ])
            values = self.env[source_model].search(domain, order=sort)
            if not values._fields.get(bridge_field):
                raise exceptions.UserError(
                    _("The target field doesn't exists in the source model"))
            if values._fields.get(bridge_field).type != 'many2one':
                raise exceptions.UserError(
                    _("The target field %s must be a Many2one") % bridge_field)
            results = values.mapped(bridge_field)
            if target_model and target_model != source_model:
                # apply security
                results = self.env[target_model].search(
                    [('id', 'in', results.ids)])
        return results

    def _get_complex_distribution_list_ids(self):
        """
        Simple case:
            no ``main_object_field`` provided
            first result list comes from ``_get_target_from_distribution_list``
            second result list is empty.
        If ``main_object_field`` is provided:
            the result ids are filtered according to the target model
            and the field specified, i.e. [trg_model.field_mailing_object.id]
        If ``main_object_domain`` is provided:
            apply a second filter
        If ``alternative_object_field`` is provided:
            a second result is computed from the first ids,
            i.e. [trg_model.alternative_object_field.id]
        If ``alternative_object_domain`` is provided:
            apply a second filter for the alternative object
        If ``sort_by`` is provided result ids are sorted accordingly
        :return: list, list
        """
        self.ensure_one()
        context = self.env.context
        mains = targets = self._get_target_from_distribution_list()
        alternatives = self.env[self.dst_model_id.model].browse()
        sort = context.get('sort_by', False)
        main_object_field = context.get('main_object_field')
        alternative_object_field = context.get('alternative_object_field')
        if main_object_field:
            main_object_domain = context.get('main_object_domain')
            main_target_model = context.get('main_target_model')
            mains = self._get_target(
                targets, main_object_field, main_object_domain,
                main_target_model, sort)
        if alternative_object_field:
            alternative_object_domain = context.get(
                'alternative_object_domain')
            alternative_target_model = context.get('alternative_target_model')
            alternatives = self._get_target(
                targets, alternative_object_field, alternative_object_domain,
                alternative_target_model, sort)
        return mains, alternatives

    def _complete_distribution_list(self, src_dist_list_ids):
        """
        Function to put include and exclude lines of given
        src_dist_list_ids (distribution.list ids) into current recordset.
        :param src_dist_list_ids: list of int
        :return:
        """
        source_dist_lists = self.env['distribution.list'].browse(
            src_dist_list_ids)
        src_lines_include = source_dist_lists.mapped(
            "to_include_distribution_list_line_ids")
        src_lines_exclude = source_dist_lists.mapped(
            "to_exclude_distribution_list_line_ids")
        lines = src_lines_include | src_lines_exclude
        for record in self:
            for line in lines:
                line.copy({
                    'distribution_list_id': record.id,
                })

    def action_show_result(self):
        """
        Show the result of the distribution list
        :return: dict/action
        """
        self.ensure_one()
        records = self._get_target_from_distribution_list()
        domain = [
            ('id', 'in', records.ids),
        ]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Result of %s') % self.name,
            'view_mode': 'tree',
            'res_model': self.dst_model_id.model,
            'context': self.env.context,
            'domain': domain,
            'target': 'current',
        }
