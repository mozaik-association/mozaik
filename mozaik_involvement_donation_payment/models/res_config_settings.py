# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    donation_account_id = fields.Many2one(
        "account.account", related="company_id.donation_account_id", readonly=False
    )
