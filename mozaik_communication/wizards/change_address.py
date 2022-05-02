# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ChangeAddress(models.TransientModel):

    _inherit = "change.address"

    def doit(self):
        """
        When changing the address, postal_bounced is set
        back to False.
        """
        super().doit()
        for wizard in self:
            wizard.partner_ids.filtered(lambda p: p.postal_bounced).write(
                {
                    "last_postal_failure_date": False,
                }
            )
