# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_volunteer = fields.Boolean(
        string="Is a volunteer",
        compute="_compute_is_volunteer",
        store=True,
        compute_sudo=True,
    )

    partner_involvement_ids = fields.One2many(
        comodel_name="partner.involvement",
        inverse_name="partner_id",
        string="Partner Involvements",
        domain=[("active", "=", True)],
    )

    partner_involvement_inactive_ids = fields.One2many(
        comodel_name="partner.involvement",
        inverse_name="partner_id",
        string="Partner Involvements (Inactive)",
        domain=[("active", "=", False)],
    )

    partner_involvement_high_ids = fields.One2many(
        comodel_name="partner.involvement",
        inverse_name="partner_id",
        string="Partner Involvements (High importance level)",
        domain=[("active", "=", True), ("importance_level", "=", "high")],
    )

    def add_involvement_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Add an involvement",
            "res_model": "partner.involvement",
            "context": {"default_partner_id": self.id},
            "view_mode": "form",
            "target": "new",
        }

    @api.depends(
        "partner_involvement_ids",
        "partner_involvement_ids.active",
        "partner_involvement_ids.involvement_type",
    )
    def _compute_is_volunteer(self):
        for partner in self:
            types = partner.partner_involvement_ids.mapped("involvement_type")
            partner.is_volunteer = "voluntary" in types
