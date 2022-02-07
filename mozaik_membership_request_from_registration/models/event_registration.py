# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EventRegistration(models.Model):

    _inherit = "event.registration"

    associated_partner_id = fields.Many2one("res.partner", string="Associated Partner")

    @api.onchange("associated_partner_id")
    def _onchange_associated_partner_id(self):
        """We want, when changing associated_partner_id, the same behavior
        we had when changing partner_id ("Booked by").
        Hence we call the same function
        """
        for registration in self:
            if registration.associated_partner_id:
                registration.update(
                    registration._synchronize_partner_values(
                        registration.associated_partner_id,
                        fnames=["lastname", "firstname", "email", "phone", "mobile"],
                    )
                )
