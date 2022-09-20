# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EventEvent(models.Model):

    _inherit = "event.event"

    def export_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "event.export.xls",
            "view_mode": "form",
            "target": "new",
            "context": {"default_event_id": self.id},
        }
