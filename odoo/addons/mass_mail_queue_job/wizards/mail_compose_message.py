# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models, _
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)

CHUNK_SIZE = 100


class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.multi
    def _prepare_vals(self):
        """
        Remove useless keys and transform all o2m list values with magic number
        """
        self.ensure_one()
        vals = self.read([
            'attachment_ids',
            'subject',
            'model',
            'reply_to',
            'composition_mode',
            'body',
            'no_auto_thread',
            'message_id',
            'author_id',
            'email_from',
            'subtype_id',
            'message_type',
        ], load='_classic_write')[0]
        vals.pop('id', None)
        for key in vals.keys():
            if isinstance(vals[key], list):
                vals[key] = [
                    (6, 0, vals[key])
                ]
        return vals

    @api.model
    def _transient_vacuum(self, force=False):
        """
        Do not unlink mail composer wizards if unfinished jobs exist
        """
        res = False
        domain = [('state', '!=', 'done')]
        jobs = self.env['queue.job'].search(domain)
        if not jobs:
            res = super()._transient_vacuum(force=force)
        return res

    @api.multi
    def send_mail(self, auto_commit=False):
        """
        Build mass mails by queue job
        """
        self.ensure_one()
        if self.composition_mode != 'mass_mail' or \
                not self._context.get('async_send_mail') or \
                not self._context.get('active_ids'):
            return super().send_mail()

        active_ids = self._context['active_ids']
        vals = self._prepare_vals()

        icp_model = self.env['ir.config_parameter']
        chunck_size = icp_model.get_param(
            'job_mail_chunck_size', default=CHUNK_SIZE)

        if not chunck_size.isdigit() or int(chunck_size) < 1:
            chunck_size = CHUNK_SIZE
            _logger.warning(
                'No valid value provided for "job_mail_chunck_size" '
                'parameter. Value %s is used.', CHUNK_SIZE)

        chunck_size = int(chunck_size)
        chunck_list_active_ids = [
            active_ids[i:i + chunck_size]
            for i in range(0, len(active_ids), chunck_size)
        ]

        wz_model = self.env['mail.compose.message']
        i = 1
        for chunck_active_ids in chunck_list_active_ids:
            description = _('Build and send mails "%s" (chunk %s/%s)') % \
                (vals['subject'], i, len(chunck_list_active_ids))
            i = i + 1
            _logger.info(
                'Delay %s for ids: %s', description, chunck_active_ids)
            wz_model.with_delay(description=description)._build_mails_jobified(
                vals, chunck_active_ids, auto_commit)
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    @job(default_channel='root.mail.build')
    def _build_mails_jobified(self, vals, active_ids, auto_commit):
        """
        Build (and send) mails
        """
        sel_ctx = self.with_context(
            async_send_mail=False, active_ids=active_ids)
        composer = sel_ctx.create(vals)
        composer.send_mail(auto_commit=auto_commit)
