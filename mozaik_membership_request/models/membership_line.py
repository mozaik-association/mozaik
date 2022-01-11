# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    def _mark_as_paid(self, amount, move_id, bank_id=False):
        res = super(MembershipLine, self)._mark_as_paid(
            amount, move_id, bank_id=bank_id
        )
        self.ensure_one()

        next_state = self.partner_id.simulate_next_state(event="paid")
        status_obj = self.env["membership.state"]
        status = status_obj.search([("code", "=", next_state)], limit=1)
        if self.state_id != status:
            self._close(force=True)
            self.flush()
            w = self.env["add.membership"].create(
                {
                    "int_instance_id": self.int_instance_id.id,
                    "partner_id": self.partner_id.id,
                    "state_id": status.id,
                }
            )
            w.action_add()

        return res

    def cron_accept_member_committee(self):
        today = fields.Date.today()
        fields.Date.to_string(today - timedelta(days=30))
        memberships = self.search(
            [
                ("state_code", "in", ["former_member_committee", "member_committee"]),
                ("date_from", "<", fields.Date.to_string(today - timedelta(days=30))),
            ]
        )
        memberships.mapped("partner_id").action_accept()
