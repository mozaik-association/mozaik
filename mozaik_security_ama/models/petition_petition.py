# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PetitionPetition(models.Model):

    _inherit = "petition.petition"

    is_private = fields.Boolean(
        string="Is private",
        help="If ticked, only members of authorized internal "
        "instances have access to the petition.",
        default=False,
        tracking=True,
    )
    int_instance_ids = fields.Many2many(
        "int.instance",
        string="Internal instances",
        help="Internal instances of the petition",
        default=lambda self: self.env.user.int_instance_m2m_ids,
        tracking=True,
    )
