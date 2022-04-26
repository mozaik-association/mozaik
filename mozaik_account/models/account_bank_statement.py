# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    def auto_reconcile(self):
        self.ensure_one()
        # remove the default_journal_id which can be added by the dashboard
        context = dict(self.env.context)
        context.pop("default_journal_id")
        self_without_default_journal_id = self.with_context(context)
        lines = self_without_default_journal_id.line_ids.filtered(
            lambda l: not (not l.partner_id or l.is_reconciled)
        )
        if not lines:
            return False
        lines._auto_reconcile()
        return True
