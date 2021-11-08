# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventQuestion(models.Model):

    _inherit = "event.question"

    interest_ids = fields.Many2many("thesaurus.term", string="Interests")
