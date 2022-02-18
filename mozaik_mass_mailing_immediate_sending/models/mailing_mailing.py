# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    def action_immediate_sending(self):
        self.write({"state": "in_queue"})
        self._process_mass_mailing_queue()
