# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    def auto_reconcile(self):
        self.ensure_one()
        self_ctx = self
        # remove the default_journal_id which can be added by the dashboard
        if "default_journal_id" in self.env.context:
            context = dict(self.env.context)
            context.pop("default_journal_id")
            self_ctx = self.with_context(context)
        lines = self_ctx.line_ids.filtered(
            lambda line: not (not line.partner_id or line.is_reconciled)
        )
        if not lines:
            return False
        lines._auto_reconcile()
        return True
