# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatement(models.Model):

    _inherit = 'account.bank.statement'

    @api.multi
    def auto_reconcile(self):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda l: not (not l.partner_id or l.journal_entry_ids))
        if not lines:
            return False
        for bank_line in lines:
            mode, __ = bank_line._get_info_from_reference(bank_line.name)
            if mode == 'membership':
                bank_line._create_membership_move(bank_line.name)
            elif mode == 'donation':
                bank_line._create_donation_move(bank_line.name)
            elif not mode:
                bank_line._create_membership_move_from_partner()
        return True
