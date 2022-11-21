# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_deceased = fields.Boolean(
        string="Deceased partner", default=False, tracking=True
    )
    death_date = fields.Date(string="Date of death", tracking=True)

    @api.constrains("death_date")
    def _check_death_date(self):
        for partner in self:
            if partner.death_date and partner.death_date > fields.Date.today():
                raise ValidationError(_("Death date cannot be in the future."))

    def write(self, vals):
        if "is_deceased" in vals:
            if vals["is_deceased"]:
                vals.update(
                    {
                        "email": False,
                        "active": False,
                        "address_address_id": False,
                    }
                )
            else:
                vals.update({"death_date": False})
        return super().write(vals)
