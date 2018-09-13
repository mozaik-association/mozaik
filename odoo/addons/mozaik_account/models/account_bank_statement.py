# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatement(models.Model):

    _inherit = 'account.bank.statement'

    @api.multi
    def auto_reconcile(self):
        self.ensure_one()
        for bank_line in self.line_ids:
            if not bank_line.partner_id or bank_line.journal_entry_ids.ids:
                continue

            mode, __, reference = bank_line._get_info_from_reference(
                bank_line.name)

            if mode == 'membership':
                bank_line._create_membership_move(reference)
            elif mode == 'donation':
                bank_line._create_donation_move(reference)
