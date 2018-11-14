# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, exceptions, fields, _


class MergeDistributionList(models.TransientModel):
    """
    Wizard to merge selected distribution lists into another distribution list
    """
    _name = 'merge.distribution.list'
    _description = 'Complete Distribution List'

    distribution_list_id = fields.Many2one(
        comodel_name="distribution.list",
        string="Distribution List",
        help="Distribution list to complete",
        required=True,
        ondelete="cascade",
    )

    @api.multi
    def merge_distribution_list(self):
        """
        Merge selected distribution list (lines) into the distribution list
        selected into the wizard
        :return: dict/action
        """
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise exceptions.UserError(
                _("Please select at least one Distribution List!"))
        self.distribution_list_id._complete_distribution_list(active_ids)
        return {}
