# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    debit_order_partner_account_id = fields.Many2one(
        comodel_name="account.account", string="Debit Order Partner Account"
    )
