# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    _inactive_cascade = True
    _allowed_inactive_link_models = ["res.partner"]

    address_address_id = fields.Many2one(
        "address.address",
        string="Address",
        index=True,
        tracking=True,
    )
    co_residency_id = fields.Many2one("co.residency", string="Co-Residency", index=True)

    address = fields.Char(
        compute="_compute_main_address_component",
        index=True,
        store=True,
        string="Address (Text)",
    )

    # Standard fields redefinition
    country_id = fields.Many2one(
        compute="_compute_main_address_component", index=True, store=True
    )
    city_id = fields.Many2one(
        compute="_compute_main_address_component", index=True, store=True
    )
    zip = fields.Char(compute="_compute_main_address_component", store=True)
    city = fields.Char(compute="_compute_main_address_component", store=True)
    street = fields.Char(compute="_compute_main_address_component", store=True)
    street2 = fields.Char(compute="_compute_main_address_component", store=True)

    @api.depends(
        "address_address_id",
        "co_residency_id",
        "co_residency_id.line",
        "co_residency_id.line2",
        "address_address_id.country_id",
        "address_address_id.city_id",
        "address_address_id.zip",
        "address_address_id.city",
        "address_address_id.street",
        "address_address_id.street2",
    )
    def _compute_main_address_component(self):
        """
        Reset address fields with corresponding main postal coordinate ids
        """
        for partner in self:
            partner.country_id = partner.address_address_id.country_id
            partner.city_id = partner.address_address_id.city_id
            partner.zip = partner.address_address_id.zip
            partner.city = partner.address_address_id.city
            partner.street = partner.address_address_id.street
            partner.street2 = partner.address_address_id.street2
            if partner.co_residency_id:
                partner.address = "%s (%s)" % (
                    partner.address_address_id.name,
                    partner.co_residency_id.display_name,
                )
            else:
                partner.address = partner.address_address_id.name

    @api.constrains("address_address_id", "co_residency_id")
    def _check_address_co_residency(self):
        self.mapped("co_residency_id")._check_partner_ids()
