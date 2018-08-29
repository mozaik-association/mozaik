# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, exceptions, fields, _


class DistributionListAddFilter(models.TransientModel):
    """
    Wizard to add filter into distribution list
    """
    _name = 'distribution.list.add.filter'
    _description = 'Add Filter Wizard'

    distribution_list_id = fields.Many2one(
        "distribution.list",
        "Distribution list",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        required=True,
        oldname="distribution_list_line_name",
    )
    exclude = fields.Boolean(
        help="Check this box to exclude filter result for the "
             "distribution list",
        default=False,
    )
    bridge_field_id = fields.Many2one(
        "ir.model.fields",
        "Bridge field",
        required=True,
        ondelete="cascade",
    )

    @api.multi
    def add_distribution_list_line(self):
        """
        Create a new distribution list line with the data filled into the
        wizard and the current active domain from the context
        :return: dict/action
        """
        self.ensure_one()
        domain = self.env.context.get('active_domain')
        active_model = self.env.context.get('active_model')
        if not domain:
            raise exceptions.UserError(
                _("You have to check the entire list to add the "
                  "current filter"))
        name = self.name
        model = self.env['ir.model'].search([
            ('model', '=', active_model)
        ], limit=1)
        self.env['distribution.list.line'].create({
            'name': name,
            'domain': domain,
            'exclude': self.exclude,
            'src_model_id': model.id,
            'bridge_field_id': self.bridge_field_id.id,
            'distribution_list_id': self.distribution_list_id.id,
        })
        return {}

    @api.multi
    def _get_valid_bridge_fields(self):
        """
        Get every fields available for each distribution.list.line
        :return: dict
        """
        self.ensure_one()
        active_model = self.env.context.get('active_model')
        dst_models = self.distribution_list_id.dst_model_id
        domain = [
            ('ttype', '=', 'many2one'),
            ('model_id.model', '=', active_model),
            ('relation', 'in', dst_models.mapped("model")),
        ]
        all_fields = self.env['ir.model.fields'].search(domain)
        available_fields = all_fields
        if active_model == dst_models.model:
            domain = [
                ('ttype', '=', 'integer'),
                ('name', '=', 'id'),
                ('model_id', '=', dst_models.id),
            ]
            all_id_fields = self.env['ir.model.fields'].search(domain)
            available_fields |= all_id_fields
        return available_fields

    @api.onchange('bridge_field_id', 'distribution_list_id')
    def _onchange_bridge_field_id(self):
        fields_available = self._get_valid_bridge_fields()
        if len(fields_available) == 1:
            self.bridge_field_id = fields_available
        if self.bridge_field_id not in fields_available:
            self.bridge_field_id = False
        result = {
            'domain': {
                'bridge_field_id': [('id', 'in', fields_available.ids)],
            },
        }
        return result
