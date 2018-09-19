# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'

    contact_ab_pc = fields.Integer()

    @api.multi
    def get_mail_values(self, res_ids):
        """
        If the wizard's model is `email.coordinate` then the recipient is the
        email of the `email.coordinate`
        """
        self.ensure_one()
        result = super().get_mail_values(res_ids)
        mailing_ids = [
            v['mailing_id']
            for v in result.values()
            if v.get('mailing_id')
        ]
        if mailing_ids:
            mailing_values = {
                'contact_ab_pc': self.contact_ab_pc,
            }
            context = self._context
            if context.get('mailing_group_id'):
                mailing_values['group_id'] = context['mailing_group_id']
            self.env['mail.mass_mailing'].browse(mailing_ids).write(
                mailing_values)
        if self.model == 'email.coordinate':
            for coord in self.env['email.coordinate'].sudo().browse(
                    result.keys()):
                email = coord.email
                if email:
                    result[coord.id].pop('recipient_ids', None)
                    result[coord.id]['email_to'] = email
        return result

    @api.multi
    def send_mail(self, auto_commit=False):
        """
        Do not recompute ids if sending mails asynchronously
        through a distribution list
        """
        self.ensure_one()
        context = self._context
        if self.distribution_list_id and \
                context.get('async_send_mail') is False:
            self = self.with_context(dl_computed=True)
        # The self could change, so specify it
        return super(MailComposeMessage, self).send_mail(
            auto_commit=auto_commit)
