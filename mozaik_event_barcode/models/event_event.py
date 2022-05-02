# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EventEvent(models.Model):

    _inherit = "event.event"

    def open_barcode_scanner(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "barcode.scanner",
            "view_mode": "form",
            "target": "new",
            "context": {"default_event_id": self.id},
        }
