# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields
from odoo.fields import first


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    distribution_list_id = fields.Many2one(
        "distribution.list",
        "Distribution list",
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

    @api.multi
    def send_mail(self):
        """
        Overriding of send mail: it has to compute the ids
        of the distribution list to send mail.
        :return: super result
        """
        context = self.env.context.copy()
        dl_computed = context.get('dl_computed')
        dist_list = self.distribution_list_id
        if dist_list and not dl_computed:
            mains, __ = dist_list._get_complex_distribution_list_ids()
            context.update({
                'active_ids': mains.ids,
                'active_model': first(mains)._name,
            })
        return super(
            MailComposeMessage, self.with_context(context)).send_mail()
