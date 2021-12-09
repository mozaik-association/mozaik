# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PetitionRegistration(models.Model):

    _inherit = "petition.registration"

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._create_membership_request_from_registration(vals)
        return rec

    def _create_membership_request_from_registration(self, vals):
        self.ensure_one()

        request = self.env["membership.request"]._create_membership_request(vals)
        request.write({"petition_registration_id": self.id})
        request._auto_validate(self.petition_id.auto_accept_membership)
