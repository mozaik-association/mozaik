# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ThesaurusTerm(models.Model):

    _name = "thesaurus.term"
    _inherit = ["mozaik.abstract.model"]
    _description = "Thesaurus Term"
    _unicity_keys = "name"

    name = fields.Char(
        string="Term",
        required=True,
        index=True,
        tracking=True,
    )

    active = fields.Boolean(
        default=True,
    )

    main_term = fields.Boolean()
