# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def create(self, vals):
        """
        If the composer is created from a mass mailing linked to
        a distribution list, add the list to the composer
        :param vals: dict
        :return: self recordset
        """
        mass_mailing_id = vals.get('mass_mailing_id')
        if mass_mailing_id:
            mass_mailing = self.env['mail.mass_mailing'].browse(
                mass_mailing_id)
            if mass_mailing.distribution_list_id:
                vals.update({
                    'distribution_list_id':
                        mass_mailing.distribution_list_id.id,
                })
        return super().create(vals)

    @api.multi
    def get_mail_values(self, res_ids):
        """
        If result of super has a `mailing_id` and `wizard` has a
        `distribution_list_id` then write into this `mail.mass_mailing` the
        found `distribution_list_id`

        **Note**
        super() result is a {key: {}}
        `mailing_id` is common for all `key`
        :param res_ids: list of int
        :return: dict
        """
        self.ensure_one()
        result = super().get_mail_values(res_ids)
        if self.distribution_list_id:
            mailing_ids = [
                v['mailing_id']
                for v in result.values()
                if v.get('mailing_id')
            ]
            if mailing_ids:
                # Only the first
                mass_mailing_obj = self.env['mail.mass_mailing']
                mass_mailing_obj.browse(mailing_ids[0]).write({
                    'distribution_list_id': self.distribution_list_id.id,
                })
        return result
