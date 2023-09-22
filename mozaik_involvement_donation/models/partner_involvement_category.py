# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PartnerInvolvementCategory(models.Model):

    _inherit = "partner.involvement.category"

    involvement_type = fields.Selection(
        selection_add=[("donation", "Donations Campaign")],
    )

    @api.onchange("involvement_type")
    def _onchange_involvement_type(self):
        super()._onchange_involvement_type()
        if self.involvement_type == "donation":
            self.allow_multi = True
