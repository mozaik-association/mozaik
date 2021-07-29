# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerRelation(models.Model):

    _inherit = 'res.partner.relation'

    email_coordinate_id = fields.Many2one(
        comodel_name='email.coordinate',
        string='Email Coordinate',
        index=True,
    )
    postal_coordinate_id = fields.Many2one(
        comodel_name='postal.coordinate',
        string='Postal Coordinate',
        index=True,
    )
    fix_coordinate_id = fields.Many2one(
        comodel_name='phone.coordinate',
        string='Fix Coordinate',
        index=True,
    )
    mobile_coordinate_id = fields.Many2one(
        comodel_name='phone.coordinate',
        string='Mobile Coordinate',
        index=True,
    )
    fax_coordinate_id = fields.Many2one(
        comodel_name='phone.coordinate',
        string='Fax Coordinate',
        index=True,
    )
    note = fields.Text(
        string='Notes',
    )
