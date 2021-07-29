# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class MergeDistributionList(models.TransientModel):
    _inherit = 'merge.distribution.list'

    @api.model
    def _default_is_newsletter(self):
        """
        Define the default value for the is_newsletter field depending on
        the context
        :return: bool
        """
        active_ids = self.env.context.get(
            'active_ids', self.env.context.get('active_id'))
        if active_ids:
            dist_list = self.env['distribution.list'].browse(active_ids)
            return all(dist_list.mapped("newsletter"))
        return False

    is_newsletter = fields.Boolean(
        "Newsletter",
        default=_default_is_newsletter,
    )
