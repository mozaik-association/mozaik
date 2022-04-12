# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    contact_ab_pc = fields.Integer(default=100)

    def get_mail_values(self, res_ids):
        """
        If the wizard's model is `email.coordinate` then the recipient is the
        email of the `email.coordinate`
        """
        self.ensure_one()
        result = super().get_mail_values(res_ids)
        mailing_ids = list(
            {v["mailing_id"] for v in result.values() if v.get("mailing_id")}
        )
        if mailing_ids:
            mailing_values = {
                "contact_ab_pc": self.contact_ab_pc,
            }
            self.env["mailing.mailing"].browse(mailing_ids).write(mailing_values)
        return result

    def send_mail(self, auto_commit=False):
        """
        Do not recompute ids if sending mails asynchronously
        through a distribution list
        """
        self.ensure_one()
        context = self._context
        if self.distribution_list_id and context.get("async_send_mail") is False:
            self = self.with_context(dl_computed=True)
        # The self could change, so specify it
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
