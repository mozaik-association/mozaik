# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResCountry(models.Model):

    _inherit = "res.country"

    def _country_default_get(self, country_code):
        return self.search([("code", "=", country_code)], limit=1)
