# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AbstractMandate(models.AbstractModel):

    _inherit = "abstract.mandate"

    gender = fields.Selection(
        related="partner_id.gender",
        readonly=True,
        store=False,
    )
