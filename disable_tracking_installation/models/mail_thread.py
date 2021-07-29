# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def _get_context_tracking(self):
        """
        Update the context in current recordset to disable tracking if the
        module is in install, test or migration,... mode.
        :return: self recordset (with new context)
        """
        self_ctx = self
        if self.env.context.get('install_mode') or self.env.all.mode:
            self_ctx = self.with_context(tracking_disable=True)
        return self_ctx

    @api.model
    def create(self, vals):
        """
        Disable tracking if possible: when testing, installing, migrating, ...
        :param vals: dict
        :return: self recordset
        """
        self_ctx = self._get_context_tracking()
        return super(MailThread, self_ctx).create(vals)

    @api.multi
    def write(self, vals):
        """
        Disable tracking if possible: when testing, installing, migrating, ...
        :param vals: dict
        :return: bool
        """
        self_ctx = self._get_context_tracking()
        return super(MailThread, self_ctx).write(vals)
