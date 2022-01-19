# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_deceased = fields.Boolean(string="Deceased partner", default=False)
    death_date = fields.Date(string="Date of death")

    @api.constrains("death_date")
    def _check_death_date(self):
        for partner in self:
            if partner.death_date and partner.death_date > fields.Date.today():
                raise ValidationError(_("Death date cannot be in the future."))

    @api.onchange("is_deceased")
    def _onchange_is_deceased(self):
        for partner in self:
            if not partner.is_deceased:
                partner.death_date = False
            else:
                partner.death_date = partner.death_date
