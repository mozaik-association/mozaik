# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventQuestion(models.Model):

    _inherit = "event.question"

    must_appear_at_scanning = fields.Boolean(
        help="If ticked, the question and its answer will be displayed when scanning "
        "the event registration barcode."
    )
