# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AddMembership(models.TransientModel):

    _inherit = "add.membership"

    def _create_membership_line(self, reference=None):
        res = super()._create_membership_line(reference)
        res._advance_in_workflow()
        return res
