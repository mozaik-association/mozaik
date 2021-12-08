# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PetitionQuestion(models.Model):

    _inherit = "petition.question"

    # invisible for simple_choice and text_input questions, visible for
    # tickbox questions and intended to be used for other types of questions
    # when inheriting this module
    involvement_category_id = fields.Many2one(
        "partner.involvement.category", string="Involvement Category"
    )


class PetitionQuestionAnswer(models.Model):

    _inherit = "petition.question.answer"

    involvement_category_id = fields.Many2one(
        "partner.involvement.category", string="Involvement Category"
    )
