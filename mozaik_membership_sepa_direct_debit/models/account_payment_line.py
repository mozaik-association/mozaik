# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentLine(models.Model):

    _inherit = "account.payment.line"

    membership_line_id = fields.Many2one(
        comodel_name="membership.line", string="Membership Line"
    )
