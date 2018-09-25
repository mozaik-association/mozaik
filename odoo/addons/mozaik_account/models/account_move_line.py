# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMoveLine(models.Model):

    _inherit = ['account.move.line']

    def create(self, vals):
        st_line_id = vals.get("statement_line_id")
        if st_line_id:
            st_line = self.env["account.bank.statement.line"].browse(
                st_line_id)
            mode, partner = st_line._get_info_from_reference(
                vals.get('name', False))
            if mode == "membership" and partner:
                vals['partner_id'] = partner.id
        return super().create(vals)
