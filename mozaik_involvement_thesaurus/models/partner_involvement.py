# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerInvolvement(models.Model):

    _inherit = "partner.involvement"

    interest_ids = fields.Many2many("thesaurus.term", string="Interests")
