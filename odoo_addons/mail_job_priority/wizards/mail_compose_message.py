# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from openerp import api, models


class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self):
        """
        Set a priority on subsequent generated mail.mail
        depending on a dictionary like:
        {limit1: prio1, limit2: prio2, ...}
        """
        if self.env.context.get('active_ids') and \
                not self.env.context.get('job_priority'):
            priorities = literal_eval(
                self.env['ir.config_parameter'].get_param(
                    'mail.sending.job.priorities', default='{}'))
            sz = len(self.env.context['active_ids'])
            limits = [lim for lim in priorities if lim <= sz]
            prio = limits and priorities[max(limits)] or None
            if prio:
                self = self.with_context(job_priority=prio)
        return super(MailComposeMessage, self).send_mail()
