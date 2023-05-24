# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerInvolvementCategory(models.Model):

    _inherit = "partner.involvement.category"

    include_in_summary = fields.Boolean(
        default=True,
        tracking=True,
        help="Check to include new involvements in the weekly summary",
    )
