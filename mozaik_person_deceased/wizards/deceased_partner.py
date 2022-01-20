# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeceasedPartner(models.TransientModel):

    _name = "deceased.partner"
    _description = "Deceased Partner"

    name = fields.Char()

    partner_id = fields.Many2one("res.partner", readonly=True)

    death_date = fields.Date(string="Date of death", required=True)

    def doit(self):
        self.ensure_one()
        self.partner_id.write(
            {
                "is_deceased": True,
                "death_date": self.death_date,
                "email": False,
                "active": False,
                "address_address_id": False,
            }
        )
