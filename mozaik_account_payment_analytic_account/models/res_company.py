# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    debit_order_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Debit Order Analytic Account"
    )
    electronic_payment_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Electronic Payment Analytic Account",
    )
