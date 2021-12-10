# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PetitionPetition(models.Model):

    _inherit = "petition.petition"

    interest_ids = fields.Many2many("thesaurus.term", string="Interests")
