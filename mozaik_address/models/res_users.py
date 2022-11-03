# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    # Change field label because there is another field with the same
    # label in HR module
    address_address_id = fields.Many2one(
        comodel_name="address.address",
        string="Personal Address",
        inherited=True,
    )
