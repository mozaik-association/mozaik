# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PetitionRegistration(models.Model):
    _inherit = "petition.registration"

    def _update_membership_request_from_registration(self, request):
        if request:
            petition_origin = self.env.ref(
                "mozaik_petition_membership_request_origin.membership_request_origin_petition"
            )
            request.write({"origin_id": petition_origin.id})
        return super()._update_membership_request_from_registration(request)
