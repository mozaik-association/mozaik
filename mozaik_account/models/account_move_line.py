# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            st_line_id = vals.get("statement_line_id")
            if st_line_id:
                mode, partner = self.env[
                    "account.bank.statement.line"
                ]._get_info_from_reference(vals.get("name", False))
                if mode in ["partner", "membership"] and partner:
                    vals["partner_id"] = partner.id
        return super().create(vals_list)

    def _remove_membership(self):
        memberships = self.env["membership.line"].search(
            [
                ("move_id", "in", self.mapped("move_id").ids),
            ]
        )
        memberships.write(
            {
                "paid": False,
                "price_paid": False,
                "move_id": False,
                "bank_account_id": False,
            }
        )

    def remove_move_reconcile(self):
        # when undoing the bank statement reconciliation
        # (will be deleted by ondelete='cascade')
        self._remove_membership()
        return super().remove_move_reconcile()

    def unlink(self):
        self._remove_membership()
        super().unlink()
