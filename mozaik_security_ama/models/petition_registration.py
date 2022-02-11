# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PetitionRegistration(models.Model):

    _inherit = "petition.registration"

    is_private = fields.Boolean(related="petition_id.is_private")

    int_instance_ids = fields.Many2many(related="petition_id.int_instance_ids")
