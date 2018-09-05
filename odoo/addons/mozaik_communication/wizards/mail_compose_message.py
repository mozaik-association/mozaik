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
            v.get('mailing_id')
            for v in result.values()
            if v.get('mailing_id')
        ]
        if mailing_ids:
            context = self._context
            mailing_values = {
                'contact_ab_pc': self.contact_ab_pc,
            }
            if context.get('mailing_group_id'):
                mailing_values['group_id'] = context['mailing_group_id']
            self.env['mail.mass_mailing'].browse(mailing_ids).write(
                mailing_values)
        email_path = context.get('email_coordinate_path', False)
        if email_path:
            for model_obj in self.env[self.model].sudo().browse(result.keys()):
                email = model_obj.mapped(email_path)
                if email:
                    result[model_obj.id].pop('recipient_ids', None)
                    result[model_obj.id]['email_to'] = email[0]
        return result

    def send_mail(self, cr, uid, ids, context=None):
        """
        Do not recompute ids if sending mails asynchronously
        """
        context = context or {}
        if not context.get('async_send_mail'):
            context = dict(context, dl_computed=True)
        return super(mail_compose_message, self).send_mail(
            cr, uid, ids, context=context)
