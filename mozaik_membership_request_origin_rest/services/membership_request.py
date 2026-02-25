# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)
trace = _logger.info


class MembershipRequestService(Component):
    _inherit = "membership.request.rest.service"

    def _validate_membership_request_input(self, input_data):
        vals = super()._validate_membership_request_input(input_data)
        if vals["origin_id"]:
            origin = self.env["membership.request.origin"].search(
                [("id", "=", vals["origin_id"])]
            )
            if origin:
                vals["origin_id"] = origin.id
            else:
                del vals["origin_id"]
                _logger.info("Unknown origin with id %s", vals["origin_id"])
        return vals
