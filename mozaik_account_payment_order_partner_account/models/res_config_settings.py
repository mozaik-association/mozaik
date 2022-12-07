# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    debit_order_partner_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Debit Order Partner Account",
        related="company_id.debit_order_partner_account_id",
        readonly=False,
    )
