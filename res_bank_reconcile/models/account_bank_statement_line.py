# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.multi
    def process_reconciliation(
            self, counterpart_aml_dicts=None, payment_aml_rec=None,
            new_aml_dicts=None):
        res = super().process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec,
            new_aml_dicts=new_aml_dicts)

        for line in self:
            if line.partner_id and \
                    line.bank_account_id and \
                    not line.bank_account_id.partner_id:
                line.bank_account_id.partner_id = line.partner_id
        return res
