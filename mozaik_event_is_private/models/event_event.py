# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventEvent(models.Model):

    _inherit = "event.event"

    is_private = fields.Boolean(string="Is Private", default=False)
