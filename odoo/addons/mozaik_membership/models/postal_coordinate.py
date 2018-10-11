# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PostalCoordinate(models.Model):

    _inherit = ['postal.coordinate']

    @api.model
    def create(self, vals):
        """
        Compute followers and change partner instance if any
        """
        change_instance = not self.env.context.get('keep_current_instance')
        res = super().create(vals)
        if res.is_main and change_instance:
            res._update_postal_follower()
        return res

    @api.model
    def write(self, vals):
        '''
        Recompute followers and change partner instance if any
        '''
        res = super().write(vals)
        if vals.get('is_main', False):
            self._update_postal_follower()
        return res

    @api.multi
    def _update_postal_follower(self):
        # self._update_partner_int_instance()
        # TODO: change instance on "main" membership if equal to int_instance
        # of previous city
        self._update_followers()
