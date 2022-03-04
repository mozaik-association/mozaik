# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

RETROCESSION_MODES_AVAILABLE = [
    ("month", "Monthly"),
    ("year", "Yearly"),
    ("none", "None"),
]
DEFAULT_RETROCESSION_MODE = "none"


class AbstractMandate(models.AbstractModel):

    _inherit = "abstract.mandate"

    retrocession_mode = fields.Selection(
        selection=RETROCESSION_MODES_AVAILABLE,
        string="Retrocession Mode",
        tracking=True,
    )
