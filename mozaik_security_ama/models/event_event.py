# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventEvent(models.Model):

    _inherit = "event.event"

    is_private = fields.Boolean(
        string="Is private",
        help="If ticked, only members of authorized internal "
        "instances have access to the event.",
        default=False,
        tracking=True,
    )

    int_instance_ids = fields.Many2many(
        "int.instance",
        string="Internal instances",
        help="Internal instances of the event",
        default=lambda self: self.env.user.int_instance_m2m_ids,
        tracking=True,
    )
