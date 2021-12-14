# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventEvent(models.Model):

    _inherit = "event.event"

    name = fields.Char(tracking=True)
    is_private = fields.Boolean(tracking=True)
    int_instance_id = fields.Many2one(tracking=True)
    note = fields.Text(tracking=True)
