# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast
from odoo import api, exceptions, models, _


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def _get_priorities(self):
        """
        Load priorities from parameters.
        As it's loaded as a json, the string must use the double quote
        and NOT simple quote.
        Ex: {"param1": 10, "param2": 20}
        :return: dict
        """
        key = 'mail.sending.job.priorities'
        try:
            priorities = ast.literal_eval(
                self.env['ir.config_parameter'].get_param(key, default='{}'))
        # Catch exception to have a understandable error message
        except (ValueError, SyntaxError):
            raise exceptions.UserError(
                _("Error to load the configuration who contains "
                  "priorities (key %s)") % key)
        # As literal_eval can transform str into any format, check if we
        # have a real dict
        if not isinstance(priorities, dict):
            raise exceptions.UserError(
                _("Error to load the configuration who contains "
                  "priorities (key %s).\nInvalid dict") % key)
        return priorities

    @api.multi
    def send_mail(self):
        """
        Set a priority on subsequent generated mail.mail, using priorities
        set into the configuration.
        :return: dict/action
        """
        active_ids = self.env.context.get('active_ids')
        default_priority = self.env.context.get('default_mail_job_priority')
        if active_ids and not default_priority:
            priorities = self._get_priorities()
            size = len(active_ids)
            limits = [lim for lim in priorities if lim <= size]
            if limits:
                prio = priorities.get(max(limits))
                self = self.with_context(default_mail_job_priority=prio)
        return super(MailComposeMessage, self).send_mail()
