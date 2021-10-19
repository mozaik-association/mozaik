# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PetitionType(models.Model):

    _name = "petition.type"
    _description = "Petition Template"
    _order = "sequence, name"

    name = fields.Char(string="Petition Template")
    sequence = fields.Integer(string="Sequence")
    question_ids = fields.One2many(
        "petition.question", "petition_type_id", string="Questions", copy=True
    )
