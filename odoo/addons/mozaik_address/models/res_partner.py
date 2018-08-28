# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class ResPartner(models.Model):

    _inherit = "res.partner"

    _inactive_cascade = True
    _allowed_inactive_link_models = ['res.partner']

    postal_coordinate_ids = fields.One2many(
        'postal.coordinate', 'partner_id', 'Postal Coordinates',
        domain=[('active', '=', True)], copy=False,
        context={'force_recompute': True})
    postal_coordinate_inactive_ids = fields.One2many(
        'postal.coordinate', 'partner_id', 'Postal Coordinates',
        domain=[('active', '=', False)], copy=False)

    postal_coordinate_id = fields.Many2one(
        "postal.coordinate", compute="_compute_main_postal_coordinate_id",
        string='Address')

    address = fields.Char(
        compute="_compute_main_address_componant", index=True, store=True)

    # Standard fields redefinition
    country_id = fields.Many2one(
        compute="_compute_main_address_componant", index=True, store=True)
    city_id = fields.Many2one(
        compute="_compute_main_address_componant", index=True, store=True)
    zip = fields.Char(
        compute="_compute_main_address_componant", store=True)
    city = fields.Char(
        compute="_compute_main_address_componant", store=True)
    street = fields.Char(
        compute="_compute_main_address_componant", store=True)
    street2 = fields.Char(
        compute="_compute_main_address_componant", store=True)

    @api.multi
    @api.depends(
        "postal_coordinate_ids",
        "postal_coordinate_ids.is_main",
        "postal_coordinate_ids.active")
    def _compute_main_postal_coordinate_id(self):
        """
        Reset main address field for a given address
        """
        coord_obj = self.env['postal.coordinate']
        coordinate_ids = coord_obj.sudo().search([
            ('partner_id', 'in', self.ids),
            ('is_main', '=', True),
            ('active', '<=', True)])
        for coord in coordinate_ids:
            if coord.active == coord.partner_id.active:
                coord.partner_id.postal_coordinate_id = coord

    @api.multi
    @api.depends(
        "postal_coordinate_ids",
        "postal_coordinate_ids.is_main",
        "postal_coordinate_ids.active")
    def _compute_main_address_componant(self):
        """
        Reset address fields with corresponding main postal coordinate ids
        """
        coord_obj = self.env['postal.coordinate']
        coordinate_ids = coord_obj.sudo().search(
            [('partner_id', 'in', self.ids),
             ('is_main', '=', True),
             ('active', '<=', True)])
        for coord in coordinate_ids:
            if coord.active == coord.partner_id.active:
                coord.partner_id.country_id = coord.address_id.country_id
                coord.partner_id.city_id = coord.address_id.city_id
                coord.partner_id.zip = coord.address_id.zip
                coord.partner_id.city = coord.address_id.city
                coord.partner_id.street = coord.address_id.street
                coord.partner_id.street2 = coord.address_id.street2
                coord.partner_id.address = 'VIP' if coord.vip else \
                    coord.address_id.name
