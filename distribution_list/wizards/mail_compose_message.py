# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    distribution_list_id = fields.Many2one(
        "distribution.list",
        "Distribution List",
        ondelete="cascade",
    )

    @api.model
    def create(self, vals):
        """
        This override allows the user to force the mass mail to
        the distribution list even if the header check-box was checked
        :param vals: dict
        :return: self recordset
        """
        context = self.env.context.copy()
        if 'distribution_list_id' in vals and 'active_domain' in context:
            context.pop('active_domain')
            if vals.get('use_active_domain'):
                vals.update({
                    'use_active_domain': False,
                    'composition_mode': 'mass_mail',
                })

        return super(
            MailComposeMessage, self.with_context(context)).create(vals)

    def send_mail(self, auto_commit=False):
        """
        With a distribution list active ids must be computed here
        except if they are previously computed.
        """
        dist_list = self.distribution_list_id
        if dist_list and not self._context.get('dl_computed'):
            mains, __ = dist_list._get_complex_distribution_list_ids()
            if mains and self._context.get('additional_res_ids'):
                additional_res_ids = self._context['additional_res_ids']
                mains |= self.env[mains._name].browse(additional_res_ids)
            self = self.with_context(
                active_ids=mains.ids,
                active_model=mains._name,
            )
        return super().send_mail(auto_commit=auto_commit)
