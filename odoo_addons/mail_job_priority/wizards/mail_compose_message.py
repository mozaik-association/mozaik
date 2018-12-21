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
        1. Mega hack to turn around a dependency impasse:
        this method always called BEFORE the same in
        distribution_list module that computes recipient ids,
        thus, compute also here the list, add dependency on distribution_list,
        set the dl_computed context and continue
        """
        if self.distribution_list_id and \
                not self.env.context.get('active_ids'):
            res_ids, _ = self.get_distribution_list_ids(
                [self.distribution_list_id.id])
            # do not send mail to an empty list of recipients
            if not res_ids:
                return {'type': 'ir.actions.act_window_close'}
            if self.env.context.get('additional_res_ids'):
                res_ids = list(
                    set(res_ids + self.env.context['additional_res_ids']))
            self = self.with_context(active_ids=res_ids, dl_computed=True)
        """
        2. Set a priority on subsequent generated mail.mail
        depending on a dictionary like:
        {limit1: prio1, limit2: prio2, ...}
        """
        if self.env.context.get('active_ids') and \
                not self.env.context.get('default_mail_job_priority'):
            priorities = literal_eval(
                self.env['ir.config_parameter'].get_param(
                    'mail.sending.job.priorities', default='{}'))
            sz = len(self.env.context['active_ids'])
            limits = [lim for lim in priorities if lim <= sz]
            prio = limits and priorities[max(limits)] or None
            if prio:
                self = self.with_context(default_mail_job_priority=prio)
        return super(MailComposeMessage, self).send_mail()
