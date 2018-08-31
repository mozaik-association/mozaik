# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

MSG_OK = "<p>Unsubscribe done successfully.</p>"
MSG_KO = "<p>The link you use to unsubscribe is no longer valid.<br/>" +\
    "Maybe your are already unsubscribed?<br/>In any case, please " +\
    "use the link available in the next email.</p>"


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    distribution_list_id = fields.Many2one(
        "distribution.list",
        "Distribution list",
    )

    @api.onchange('mailing_model_id', 'contact_list_ids')
    def _onchange_model_and_list(self):
        result = super()._onchange_model_and_list()
        self.distribution_list_id = False
        return result

    def _try_update_opt(self, res_id):
        """
        Try to find a distribution list and call 'update_opt' with the passed
        'res_id' as 'partner_id'
        :param res_id: int
        :return: str
        """
        self.ensure_one()
        if self.exists() and res_id and self.distribution_list_id:
            dist_list = self.distribution_list_id
            already_opt_out = dist_list.res_partner_opt_out_ids.ids
            if int(res_id) not in already_opt_out:
                dist_list._update_opt([res_id])
                return MSG_OK
        return MSG_KO
