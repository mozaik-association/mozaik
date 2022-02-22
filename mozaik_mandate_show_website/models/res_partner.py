# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    no_show_mandates = fields.Boolean(
        string="Don't show mandates on website",
        help="Don't show any mandate from this partner on website.",
    )
