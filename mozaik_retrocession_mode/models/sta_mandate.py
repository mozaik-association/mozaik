# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from .abstract_mandate import DEFAULT_RETROCESSION_MODE


class StaMandate(models.Model):

    _inherit = "sta.mandate"

    retrocession_mode = fields.Selection(
        required=True,
        default=DEFAULT_RETROCESSION_MODE,
    )
