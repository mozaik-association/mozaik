# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventRegistration(models.Model):

    _inherit = "event.registration"

    zip = fields.Char(string="Zipcode", help="Manual zipcode")

    def _get_website_registration_allowed_fields(self):
        res = super()._get_website_registration_allowed_fields()
        res.update(["zip", "mobile"])
        return res
