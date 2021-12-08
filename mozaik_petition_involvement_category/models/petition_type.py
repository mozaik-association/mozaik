# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PetitionType(models.Model):

    _inherit = "petition.type"

    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category", string="Involvement Category"
    )
