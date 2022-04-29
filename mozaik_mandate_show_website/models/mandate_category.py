# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MandateCategory(models.Model):

    _inherit = "mandate.category"

    no_show_on_website = fields.Boolean(
        string="Don't show mandates",
        help="Don't show mandates having this mandate category on website.",
    )
