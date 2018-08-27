# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, exceptions, fields, _
from odoo.osv import expression


class DistributionList(models.Model):
    """
    New Odoo model used to represents a distribution list (to send email or
    postal mails).
    """
    _name = 'distribution.list'
    _description = 'Distribution List'

    name = fields.Char(
        required=True,
    )
    to_include_distribution_list_line_ids = fields.One2many(
        "distribution.list.line",
        "distribution_list_id",
        "Filters to include",
        domain=[('exclude', '!=', True)],
    )
    to_exclude_distribution_list_line_ids = fields.One2many(
        "distribution.list.line",
        "distribution_list_id",
        "Filters to exclude",
        domain=[('exclude', '=', True)],
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env['res.company']._company_default_get(
            self._name),
    )
    dst_model_id = fields.Many2one(
        "ir.model",
        "Destination model",
        required=True,
        default=lambda self: self.env.ref("base.model_res_partner").id,
    )
    bridge_field = fields.Char(
        required=True,
        help="Field name making the bridge between source model of filters "
             "and target model of distribution list",
        default='id',
    )
    note = fields.Text(
    )

    _sql_constraints = [
        ('constraint_uniq_name', 'unique(company_id, name)',
         "This name already exists for this company"),
    ]

    @api.model
    def _get_computed_targets(self, bridge_field, targets, in_mode):
        """
        Convert source ids to target ids according to the bridge field
        :param bridge_field: str
        :param targets: dict
        :param in_mode: bool
        :return: target recordset
        """
        if not bridge_field or bridge_field == 'id':
            return targets
        elif not targets._fields.get(bridge_field):
            # Ensure the bridge field exists into the target model
            raise exceptions.UserError(
                _("The target model (%s) doesn't contain the bridge field: "
                  "%s") % (targets._name, bridge_field))
        elif targets._fields.get(bridge_field).type == 'many2one':
            return targets.mapped(bridge_field)
        raise exceptions.UserError(
            _("The bridge field must be a Many2one!"))

    @api.multi
    def _get_target_if_no_included_filter(self):
        target_model = self.mapped("dst_model_id").model
        return self.env[target_model].browse()

    @api.multi
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
        result._complete_distribution_list(self.ids)
        return result

    @api.multi
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

    @api.multi
    def _get_target_from_distribution_list(self, safe_mode=True):
        """
        This method computes all filters result and return a list of ids
        depending of the ``bridge_field`` of the distribution list.
        safe_mode:  Tool used in case of multiple distribution list.
                    If a filter is include into a distribution list
                    and exclude into an other then the result depends
                    of `safe_mode`.
                    True: excluded are not present
                    False: excluded will be present if included into an other
        :param safe_mode: bool
        :return: target recordset
        """
        self.ensure_one()
        bridge_field = self.bridge_field
        include_dll = self.to_include_distribution_list_line_ids
        exclude_dll = self.to_exclude_distribution_list_line_ids
        if not include_dll:
            # without included filters get all ids
            # from a method to override
            results_include = self._get_target_if_no_included_filter()
        else:
            # get all ids to include
            results_include = include_dll._get_target_recordset()

        # get all ids to exclude
        if exclude_dll:
            results_exclude = exclude_dll._get_target_recordset()
        # If the exclude_dll is empty, we have to build an empty recordset
        # with the same include's model
        else:
            results_exclude = self.env[results_include._name].browse()

        if not safe_mode:
            # compute ids locally for only one distribution list
            results = self._get_computed_targets(
                bridge_field, results_include, in_mode=True)
            if results_exclude:
                results -= self._get_computed_targets(
                    bridge_field, results_exclude, in_mode=False)
            results_include = False
            results_exclude = False

        if bridge_field and safe_mode:
            # compute ids globally for all distribution lists
            results = self._get_computed_targets(
                bridge_field, results_include, in_mode=True)
            if results_exclude:
                results -= self._get_computed_targets(
                    bridge_field, results_exclude, in_mode=False)

        return results

    @api.model
    def _get_target(self, source_records, bridge_field, domain, sort):
        """
        From an initial list of ids of a model, returns a list
        containing the value of a specific field of this model
        optionally filtered by an extra domain and/or
        ordered by a given sort criteria
        Final result is a list of unique values (sorted or not)
        If no target field is given the initial ids list is returned
        :param source_records: recordset
        :param bridge_field: str
        :param domain: list
        :param sort: str
        :return: recordset
        """
        target_model = source_records._name
        if not bridge_field:
            results = source_records
        elif not source_records._fields.get(bridge_field):
            raise exceptions.UserError(
                _("The target model %s doesn't have a field named "
                  "%s") % (target_model, bridge_field))
        elif source_records:
            domain = domain or []
            domain = expression.AND([
                domain,
                [
                    ('id', 'in', source_records.ids),
                    (bridge_field, '!=', False),
                ],
            ])
            values = self.env[target_model].search(domain, order=sort)
            if not values._fields.get(bridge_field):
                raise exceptions.UserError(
                    _("The target field doesn't exists in the source model"))
            if values._fields.get(bridge_field).type != 'many2one':
                raise exceptions.UserError(
                    _("The target field %s must be a Many2one") % bridge_field)
            results = values.mapped(bridge_field)
        else:
            results = self.env[target_model].browse()
        return results

    @api.multi
    def _get_complex_distribution_list_ids(self):
        """
        Simple case:
            no ``field_main_object`` provided
            first result list is coming from ``get_ids_from_distribution_list``
            second result list is empty.
        If ``field_main_object`` is provided:
            the result ids are filtered according to the target model
            and the field specified, i.e. [trg_model.field_mailing_object.id]
        If ``more_filter`` is provided:
            apply a second filter
        If ``field_alternative_object`` is provided:
            a second result is computed from the first ids,
            i.e. [trg_model.field_alternative_object.id]
        If ``alternative_more_filter`` is provided:
            apply a second filter for the alternative object
        If ``sort_by`` is provided result ids are sorted accordingly
        :return: list, list
        """
        self.ensure_one()
        context = self.env.context
        targets = self._get_target_from_distribution_list()
        sort = context.get('sort_by', False)
        field_main_object = context.get('field_main_object')
        more_filter = context.get('more_filter')
        field_alternative_object = context.get('field_alternative_object')
        alternative_more_filter = context.get('alternative_more_filter')
        mains = self._get_target(targets, field_main_object, more_filter, sort)
        alternatives = self._get_target(
            targets, field_alternative_object, alternative_more_filter, sort)
        return mains, alternatives

    @api.multi
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

    @api.multi
    def get_action_from_domains(self):
        """
        Allow to preview resulting of distribution list
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
            'view_mode': 'tree, form',
            'res_model': self.dst_model_id.model,
            'context': self.env.context.copy(),
            'domain': domain,
            'target': 'current',
        }
