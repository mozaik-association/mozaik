# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, _


class MailMailStats(models.Model):
    _inherit = 'mail.mail.statistics'

    def set_bounced(self, mail_mail_ids=None, mail_message_ids=None):
        """
        Increase the bounce counter of the email_coordinate
        :param mail_mail_ids: list of int
        :param mail_message_ids: list of int
        :return: self recordset
        """
        results = super(MailMailStats, self).set_bounced(
            mail_mail_ids=mail_mail_ids, mail_message_ids=mail_message_ids)
        active_ids = []
        active_model = 'email.coordinate'
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
                wizard = self.env['failure.editor'].with_context(ctx).create({
                    'increase': 1,
                    'description': _('Invalid Email Address'),
                })
                wizard.update_failure_data()
                # post technical details of the bounce on the sender document
                keep_bounce = self.env['ir.config_parameter'].get_param(
                    'mail.bounce.keep', default='1')
                bounce_body = ctx.get('bounce_body')
                if bounce_body and keep_bounce.lower() in ['1', 'true']:
                    email_coordinate = self.env[active_model].browse(
                        active_ids)
                    email_coordinate.message_post(
                        subject='Bounce Details', body=bounce_body)
        return results
