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
    sponsorship_date = fields.Date()

    @api.constrains("sponsor_id")
    def check_parent_different_from_self(self):
        for rec in self:
            if rec.sponsor_id == rec:
                raise ValidationError(_("A partner cannot be sponsored by itself"))

    @api.constrains("sponsor_id", "sponsorship_date")
    def check_sponsorship_date_only_if_sponsor(self):
        for rec in self:
            if rec.sponsorship_date and not rec.sponsor_id:
                raise ValidationError(
                    _("A partner with a sponsorship date must have a sponsor.")
                )

    @api.onchange("sponsor_id")
    def _onchange_sponsorship_date(self):
        for rec in self:
            if not rec.sponsor_id:
                rec.sponsorship_date = False
            elif rec.sponsor_id and not rec._origin.sponsor_id:
                rec.sponsorship_date = fields.Date.today()

    def write(self, vals):
        """
        * When writing a sponsor for the first time -> Default value for
        sponsorship date is today
        * When deleting a sponsor -> Sponsorship date must be set back to False
        """
        if "sponsor_id" in vals:
            if not vals["sponsor_id"]:
                vals["sponsorship_date"] = False
                return super().write(vals)
            if "sponsorship_date" not in vals:
                partners_with_sponsor = self.filtered("sponsor_id")
                res = super(ResPartner, partners_with_sponsor).write(vals)
                vals_copy = vals.copy()
                vals_copy["sponsorship_date"] = fields.Date.today()
                res2 = super(ResPartner, self - partners_with_sponsor).write(vals_copy)
                return res and res2

        return super().write(vals)
