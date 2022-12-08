# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    def mark_as_unpaid(self):
        self.write(
            {
                "paid": False,
                "price_paid": False,
                "move_id": False,
                "bank_account_id": False,
            }
        )
