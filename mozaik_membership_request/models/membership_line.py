# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
from datetime import timedelta

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class MembershipLine(models.Model):

    _inherit = "membership.line"

    @api.model
    def _get_states_put_amount_on_membership(self):
        """
        For some membership states, we want to set the amount on the
        membership line.
        :return: list of membership state codes for which the amount
        must be written on the membership line.
        Intended to be extended.
        """
        return ["former_member"]

    def _mark_as_paid(self, amount, move_id, bank_id=False):
        self.ensure_one()
        previous_state = self.partner_id.membership_state_code
        next_state = self.partner_id.simulate_next_state(event="paid")
        status_obj = self.env["membership.state"]
        status = status_obj.search([("code", "=", next_state)], limit=1)

        # when it's a former member, we want to pay the newlly created membership
        membership = self
        states_mark_amount = self._get_states_put_amount_on_membership()
        if self.state_id != status and previous_state in states_mark_amount:
            membership = self.create_following_membership(status, amount)

        res = super(MembershipLine, membership)._mark_as_paid(
            amount, move_id, bank_id=bank_id
        )

        if self.state_id != status and previous_state not in states_mark_amount:
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

    def _advance_in_workflow(self):
        self.ensure_one()
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
            and self.price == 0
            and self.paid
        ):
            # If creating a free membership line, we want to trigger the
            # same workflow as when a not free membership line is marked as paid,
            # i.e. creating the following membership (following the statechart)
            next_state = self.partner_id.simulate_next_state(event="paid")
            status_obj = self.env["membership.state"]
            status = status_obj.search([("code", "=", next_state)], limit=1)
            if self.state_id != status:
                self.create_following_membership(status)

    def cron_accept_member_committee(self):
        today = fields.Date.today()
        days = int(
            self.env["ir.config_parameter"].get_param(
                "number_days_accept_member_committee", default=30
            )
        )
        date_from = fields.Date.to_string(today - timedelta(days=days))
        memberships = self.search(
            [
                ("state_code", "in", ["former_member_committee", "member_committee"]),
                ("date_from", "<", date_from),
                ("active", "=", True),
            ]
        )
        memberships.mapped("partner_id").filtered(
            lambda p: not p.suspend_member_auto_validation
        ).action_accept()

    def cron_member_candidate_to_supporter(self):
        today = fields.Date.today()
        days = int(
            self.env["ir.config_parameter"].get_param(
                "number_days_member_candidate_to_supporter", default=90
            )
        )
        date_from = fields.Date.to_string(today - timedelta(days=days))
        memberships = self.search(
            [
                ("state_code", "=", "member_candidate"),
                ("date_from", "<", date_from),
                ("active", "=", True),
            ]
        )
        memberships.action_invalidate()
        supporter_state = self.env["membership.state"].search(
            [("code", "=", "supporter")]
        )
        for m in memberships:
            m.partner_id.write(
                {
                    "message_ids": [
                        (
                            0,
                            0,
                            {
                                "subject": _("Automatic membership state change"),
                                "body": _(
                                    "Partner with id %(partner_id)s is member candidate "
                                    "since more than %(days)s days "
                                    "and didn't pay: he becomes a supporter."
                                    % {"days": days, "partner_id": m.partner_id.id}
                                ),
                                "message_type": "comment",
                                "model": "res.partner",
                                "res_id": m.partner_id.id,
                            },
                        )
                    ]
                }
            )

            self.env["add.membership"].create(
                {
                    "partner_id": m.partner_id.id,
                    "int_instance_id": m.int_instance_id.id,
                    "state_id": supporter_state.id,
                }
            ).action_add()
