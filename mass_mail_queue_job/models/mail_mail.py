# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo
from odoo import models


class MailMail(models.Model):

    _inherit = "mail.mail"

    def send(self, auto_commit=False, raise_exception=False):
        """Do not send mails otherwise than by job except if explicitly force
        It is because mass_mail composition mode of mail.compose.message
        sends emails directly in V11 without using "Email Queue Manager".
        """
        res = None
        # ignore this behavior in test, it create bugs in some addons
        send_it = self._context.get("force_send") or odoo.tools.config["test_enable"]
        if not send_it and self._context.get("job_uuid"):
            job = self.env["queue.job"].search(
                [("uuid", "=", self._context["job_uuid"])]
            )
            if job:
                send_it = job.method_name == "_send_mail_jobified"
        if send_it:
            res = super().send(auto_commit=auto_commit, raise_exception=raise_exception)
        return res
