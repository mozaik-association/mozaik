# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _


class MailMailStats(models.Model):
    _inherit = 'mail.mail.statistics'

    def set_bounced(self, mail_mail_ids=None, mail_message_ids=None):
        """
        Increase the bounce counter of the email_coordinate
        :param mail_mail_ids: list of int
        :param mail_message_ids: list of int
        :return: self recordset
        """
        results = super().set_bounced(
            mail_mail_ids=mail_mail_ids, mail_message_ids=mail_message_ids)
        active_ids = []
        active_model = 'res.partner'
        for record in self:
            target_obj = self.env[record.model]
            if record.model == active_model and record.res_id:
                active_ids = [record.res_id]
            else:
                email_key = target_obj._get_relation_column_name(active_model)
                if email_key:
                    target = target_obj.browse(record.res_id)[email_key]
                    active_ids = target.ids

            if active_ids:
                ctx = self.env.context.copy()
                ctx.update({
                    'active_ids': active_ids,
                    'active_model': active_ids,
                })
                wizard = self.env['failure.editor'].with_context(ctx).create({ # TODO wizrd doesnt' exist enymore
                    'increase': 1,
                    'description': _('Invalid Email Address'),
                })
                wizard.update_failure_data()
                # post technical details of the bounce on the sender document
                keep_bounce = self.env['ir.config_parameter'].sudo().get_param(
                    'mail.bounce.keep', default='1')
                bounce_body = ctx.get('bounce_body')
                if bounce_body and keep_bounce.lower() in ['1', 'true']:
                    partner = self.env[active_model].browse(
                        active_ids)
                    partner.message_post(
                        subject=_('Bounce Details'), body=bounce_body)
        return results
