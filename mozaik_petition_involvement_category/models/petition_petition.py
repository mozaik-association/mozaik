# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PetitionPetition(models.Model):

    _inherit = "petition.petition"

    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category",
        string="Involvement Category",
        compute="_compute_involvement_category_id",
        store=True,
        readonly=False,
    )

    @api.depends("petition_type_id")
    def _compute_involvement_category_id(self):
        """Update petition configuration from its petition type. Depends are set only
        on petition_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if petition type is changed, update petition configuration. Changing
        petition type content itself should not trigger this method."""
        for petition in self:
            if (
                petition.petition_type_id
                and petition.petition_type_id.involvement_category_id
            ):
                petition.involvement_category_id = (
                    petition.petition_type_id.involvement_category_id
                )
            else:
                petition.involvement_category_id = False
