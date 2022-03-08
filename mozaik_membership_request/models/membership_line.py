# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    def _mark_as_paid(self, amount, move_id, bank_id=False):
        self.ensure_one()
        previous_state = self.partner_id.membership_state_code
        next_state = self.partner_id.simulate_next_state(event="paid")
        status_obj = self.env["membership.state"]
        status = status_obj.search([("code", "=", next_state)], limit=1)

        # when it's a former member, we want to pay the newlly created membership
        membership = self
        if self.state_id != status and previous_state == "former_member":
            membership = self.create_following_membership(status, amount)

        res = super(MembershipLine, membership)._mark_as_paid(
            amount, move_id, bank_id=bank_id
        )

        if self.state_id != status and previous_state != "former_member":
            self.create_following_membership(status)

        return res

    def create_following_membership(self, status, amount=False):
        self.ensure_one()
        self._close(force=True)
        self.flush()
        vals = {
            "int_instance_id": self.int_instance_id.id,
            "partner_id": self.partner_id.id,
            "state_id": status.id,
            "product_id": self.product_id.id,
        }
        if amount:
            vals["price"] = amount
        w = self.env["add.membership"].create(vals)
        return w._create_membership_line()

    def cron_accept_member_committee(self):
        today = fields.Date.today()
        fields.Date.to_string(today - timedelta(days=30))
        memberships = self.search(
            [
                ("state_code", "in", ["former_member_committee", "member_committee"]),
                ("date_from", "<", fields.Date.to_string(today - timedelta(days=30))),
                ("active", "=", True),
            ]
        )
        memberships.mapped("partner_id").action_accept()
