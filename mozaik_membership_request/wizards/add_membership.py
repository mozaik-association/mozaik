# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json

from odoo import models


class AddMembership(models.TransientModel):

    _inherit = "add.membership"

    def _create_membership_line(self, reference=None):
        res = super()._create_membership_line(reference)

        # The statechart is defined but lives independently of the record
        # This was not the best way to do that when migrating but
        # to avoid refactoring the whole code, we force the configuration,
        # setting the current membership state to trigger the right
        # computation of sc_<event>_allowed fields.
        self.sudo().partner_id.sc_state = json.dumps(
            {"configuration": ["root", self.partner_id.membership_state_id.code]}
        )

        if (
            self.product_id.advance_workflow_as_paid
            and self.partner_id.sc_paid_allowed
            and res.price == 0
            and res.paid
        ):
            # If creating a free membership line, we want to trigger the
            # same workflow as when a not free membership line is marked as paid,
            # i.e. creating the following membership (following the statechart)
            next_state = self.partner_id.simulate_next_state(event="paid")
            status_obj = self.env["membership.state"]
            status = status_obj.search([("code", "=", next_state)], limit=1)
            if res.state_id != status:
                res.create_following_membership(status)

        return res
