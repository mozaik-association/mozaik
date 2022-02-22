# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventEvent(models.Model):

    _inherit = "event.event"

    domain = fields.Text(
        string="Target partners domain",
        help="Add a domain on partners model to limit the access of this event.",
        default="[]",
    )
