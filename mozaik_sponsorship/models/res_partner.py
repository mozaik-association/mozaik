# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = "res.partner"

    sponsor_id = fields.Many2one("res.partner", string="Sponsor", index=True)
    sponsor_godchild_ids = fields.One2many(
        "res.partner",
        "sponsor_id",
        string="Sponsor Godchildren",
        domain=[("active", "=", True)],
    )

    @api.constrains("sponsor_id")
    def check_parent_different_from_self(self):
        for rec in self:
            if rec.sponsor_id == rec:
                raise ValidationError(_("A partner cannot be sponsored by itself"))
