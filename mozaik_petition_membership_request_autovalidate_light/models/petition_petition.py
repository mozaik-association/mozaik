# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PetitionPetition(models.Model):

    _inherit = "petition.petition"

    autovalidation_type = fields.Selection(
        [("light", "Light"), ("complete", "Complete")], default="complete"
    )
