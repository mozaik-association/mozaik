# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventStage(models.Model):

    _inherit = "event.stage"

    draft_stage = fields.Boolean(string="Draft Stage")
