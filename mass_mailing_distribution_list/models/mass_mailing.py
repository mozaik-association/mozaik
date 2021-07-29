# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    distribution_list_id = fields.Many2one(
        comodel_name="distribution.list",
        string="Distribution List",
    )

    @api.onchange('mailing_model_id', 'contact_list_ids')
    def _onchange_model_and_list(self):
        result = super()._onchange_model_and_list()
        self.distribution_list_id = False
        return result

    @api.multi
    def update_opt_out(self, email, res_ids, value):
        """
        Unsubscribe from distribution list if any
        :param email: string
        :param res_ids: list
        :param value: boolean
        """
        self.ensure_one()
        if self.distribution_list_id:
            # opt-out is delegated to the distribution list
            return self.distribution_list_id._update_opt(res_ids)
        return super().update_opt_out(email, res_ids, value)
