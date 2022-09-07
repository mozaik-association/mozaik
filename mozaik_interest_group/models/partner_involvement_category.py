# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerInvolvementCategory(models.Model):

    _inherit = "partner.involvement.category"

    interest_group_ids = fields.Many2many(
        "interest.group", string="Interest groups", tracking=True
    )
