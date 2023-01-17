# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    debit_order_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Debit Order Analytic Account",
        related="company_id.debit_order_analytic_account_id",
        readonly=False,
    )
    electronic_payment_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Electronic Payment Analytic Account",
        related="company_id.electronic_payment_analytic_account_id",
        readonly=False,
    )
