# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventEvent(models.Model):

    _inherit = "event.event"

    auto_accept_membership = fields.Boolean(
        string="Accept membership requests",
        help="Membership requests that can be linked to a "
        "unique existing partner are automatically accepted.",
        default=True,
    )
