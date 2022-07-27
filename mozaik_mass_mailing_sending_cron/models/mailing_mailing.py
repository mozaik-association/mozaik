# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    def _process_mass_mailing_queue(self):
        super(
            MailingMailing,
            self.with_context(
                lang=self.env.context.get("lang", False) or self.env.user.lang
            ),
        )._process_mass_mailing_queue()
