# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_donor = fields.Boolean(
        string="Is a donor",
        compute="_compute_involvement_bools",
        store=True,
        compute_sudo=True,
    )
    is_volunteer = fields.Boolean(
        string="Is a volunteer",
        compute="_compute_involvement_bools",
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
        "partner_involvement_inactive_ids",
        "partner_involvement_inactive_ids.active",
        "partner_involvement_inactive_ids.involvement_type",
    )
    def _compute_involvement_bools(self):
        for partner in self:
            types = partner.partner_involvement_ids.mapped("involvement_type")
            partner.is_donor = "donation" in types
            partner.is_volunteer = "voluntary" in types

    def get_all_involvements_partner_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "All Involvements",
            "res_model": "partner.involvement",
            "context": {
                "search_default_partner_id": self.id,
                "default_partner_id": self.id,
                "search_default_all": True,
            },
            "view_mode": "tree,form",
        }

    def get_donations_partner_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Donations",
            "res_model": "partner.involvement",
            "context": {
                "search_default_partner_id": self.id,
                "default_partner_id": self.id,
                "search_default_creation_time_year": 1,
                "search_default_donation": 1,
            },
            "domain": [("involvement_type", "=", "donation")],
            "view_mode": "tree,form",
        }
