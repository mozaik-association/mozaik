# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PetitionRegistration(models.Model):

    _inherit = "petition.registration"

    def _create_membership_request_from_registration(self, vals):
        self.ensure_one()
        mr_vals = vals.copy()
        mr_vals["autovalidation_type"] = self.petition_id.autovalidation_type
        return super()._create_membership_request_from_registration(mr_vals)
