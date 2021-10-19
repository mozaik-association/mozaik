# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PetitionMilestone(models.Model):

    _name = "petition.milestone"
    _description = "Milestones to reach when singing up"

    value = fields.Integer(string="Value")
    petition_id = fields.Many2one("petition.petition", string="Related Petition")
