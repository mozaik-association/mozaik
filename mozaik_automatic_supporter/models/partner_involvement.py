# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PartnerInvolvement(models.Model):

    _inherit = "partner.involvement"

    @api.model
    def create(self, vals):
        """
        if any, for automatic supporter, advance the partner's workflow
        """
        res = super(PartnerInvolvement, self).create(vals)
        if (
            res.involvement_category_id.automatic_supporter
            and res.partner_id.membership_state_code in (False, "without_membership")
        ):
            vals = self.env["membership.request"]._get_status_values(
                "s", date_from=res.creation_time
            )
            res.partner_id.write(vals)
            next_state = self.env["membership.state"].search(
                [("code", "=", res.partner_id.simulate_next_state())], limit=1
            )
            if next_state:
                w = self.env["add.membership"].create(
                    {
                        "int_instance_id": res.partner_id.int_instance_id.id,
                        "partner_id": res.partner_id.id,
                        "state_id": next_state.id,
                    }
                )
                w.action_add()
        return res
