# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AllowIncompatibleMandateWizard(models.TransientModel):

    _inherit = 'allow.duplicate.wizard'
    _name = "allow.incompatible.mandate.wizard"

    def button_allow_duplicate(self):
        super().button_allow_duplicate()

        # redirect to the representative's form view
        ids = self.env.context.get('active_ids')
        generic_mandate = self.env["generic.mandate"].browse(ids[0])
        return generic_mandate.partner_id.get_formview_action()
