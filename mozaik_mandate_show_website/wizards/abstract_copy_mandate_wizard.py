# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class AbstractCopyMandateWizard(models.TransientModel):

    _inherit = "abstract.copy.mandate.wizard"
    _description = "Abstract Copy Mandate Wizard"

    def _copy_mandate(self, vals):
        if self.mandate_category_id and self.mandate_category_id.no_show_on_website:
            vals["no_show_on_website"] = True
        return super()._copy_mandate(vals)
