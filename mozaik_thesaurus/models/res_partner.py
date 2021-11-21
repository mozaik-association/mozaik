# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _name = "res.partner"
    _inherit = ["res.partner"]
    _terms = ["interest_ids", "competency_ids"]

    competency_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        relation="res_partner_term_competencies_rel",
        column1="partner_id",
        column2="thesaurus_term_id",
    )
    interest_ids = (
        fields.Many2many(
            comodel_name="thesaurus.term",
            relation="res_partner_term_interests_rel",
            column1="partner_id",
            column2="thesaurus_term_id",
        ),
    )
    indexation_comments = fields.text("Comments")
