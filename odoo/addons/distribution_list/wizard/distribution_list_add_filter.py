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
        default=lambda self: self.env.context.get('distribution_list_id'),
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
    )

    @api.multi
    def _add_distribution_list_line(self):
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
        name = self.distribution_list_line_name
        model = self.env['ir.model'].search([
            ('model', '=', active_model)
        ], limit=1)
        self.env['distribution.list.line'].create({
            'name': name,
            'domain': domain,
            'exclude': self.exclude,
            'src_model_id': model.id,
            'distribution_list_id': self.distribution_list_id.id,
        })
        return {}
