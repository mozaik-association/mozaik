# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def _update_membership_request_from_registration(self, request):
        if request:
            event_origin = self.env.ref(
                "mozaik_event_membership_request_origin.membership_request_origin_event"
            )
            request.write({"origin_id": event_origin.id})
        return super()._update_membership_request_from_registration(request)
