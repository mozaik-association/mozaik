# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _name = "res.partner"
    _inherit = ["res.partner", "statechart.mixin"]
    _statechart_file = "mozaik_membership_request/data/res_partner_statechart.yml"

    accepted_date = fields.Date()
    free_member = fields.Boolean()
    decline_payment_date = fields.Date()
    rejected_date = fields.Date()
    resignation_date = fields.Date()
    exclusion_date = fields.Date()

    suspend_member_auto_validation = fields.Boolean(
        help="If ticked, the scheduled action will not automatically validate "
        "the Member membership line of this partner."
    )

    def simulate_next_state(self, event=None):
        self.ensure_one()
        self.sudo().sc_state = json.dumps(
            {"configuration": ["root", self.membership_state_code]}
        )
        if event:
            getattr(self, event)()
        interpreter = self.sc_interpreter
        transitions = interpreter._statechart.transitions
        evaluator = interpreter._evaluator
        # reload the states in case the event have changed it
        states = json.loads(self.sc_state)["configuration"]
        states.remove("root")
        next_state = states[0]
        for transition in transitions:
            if not transition.event and transition.source in interpreter._configuration:
                if transition.guard is None:
                    next_state = transition.target
                    break
                try:
                    if evaluator.evaluate_guard(transition, None):
                        next_state = transition.target
                        break
                except Exception:  # pylint: disable=broad-except
                    # Guard could not be evaluated
                    continue
        return next_state

    def button_modification_request(self):
        """
        Create a `membership.request` from a partner
        """
        self.ensure_one()
        membership_request = self.env["membership.request"]
        mr = membership_request.search(
            [("partner_id", "=", self.id), ("state", "=", "draft")]
        )
        if not mr:
            address_id = self.address_address_id
            birthdate_date = self.birthdate_date
            day = False
            month = False
            year = False
            if birthdate_date:
                day = birthdate_date.day
                month = birthdate_date.month
                year = birthdate_date.year

            state_id = self.membership_state_id.id or False
            competencies = self.competency_ids
            values = {
                "membership_state_id": state_id,
                "result_type_id": state_id,
                "identifier": self.identifier,
                "lastname": self.lastname,
                "firstname": self.firstname,
                "gender": self.gender,
                "birthdate_date": birthdate_date,
                "day": day,
                "month": month,
                "year": year,
                "is_update": True,
                "country_id": address_id.country_id.id or False,
                "address_local_street_id": (
                    address_id.address_local_street_id.id or False
                ),
                "street_man": address_id.street_man or False,
                "street2": address_id.street2 or False,
                "city_id": (address_id.city_id.id or False),
                "zip_man": address_id.zip_man or False,
                "city_man": address_id.city_man or False,
                "box": address_id.box or False,
                "number": address_id.number or False,
                "mobile": self.mobile or False,
                "phone": self.phone or False,
                "email": self.email or False,
                "partner_id": self.id,
                "address_id": address_id.id or False,
                "int_instance_ids": [(6, 0, self.int_instance_ids.ids)],
                "interest_ids": [(6, 0, self.interest_ids.ids)],
                "competency_ids": [(6, 0, competencies.ids)],
                "nationality_id": self.nationality_id.id or False,
            }
            # create mr in sudo mode for portal user allowing to avoid create
            # rights on this model for these users
            if "default_open_partner_user" in self.env.context:
                membership_request = membership_request.sudo()
            mr = membership_request.create(values)
        res = mr.get_formview_action()
        return res

    def pay_membership(self, amount_paid, move_id, bank_account_id):
        res = super(ResPartner, self).pay_membership(
            amount_paid, move_id, bank_account_id
        )

        next_state = self.simulate_next_state(event="paid")
        status_obj = self.env["membership.state"]
        status = status_obj.search([("code", "=", next_state)], limit=1)
        membership = self.env["membership.line"].search(
            [
                ("id", "in", self.membership_line_ids.ids),
                ("active", "=", True),
                ("state_code", "in", ["former_member", "supporter"]),
            ],
            limit=1,
        )
        if self.membership_state_id != status and membership:
            # reference must be unique, so remove it from the last membership
            last_member_membership = self.env["membership.line"].search(
                [
                    ("reference", "=", self.reference),
                ],
                limit=1,
            )
            last_member_membership.reference = False
            if membership.state_code != "former_member":
                # keep the paid for former member, since we will pay the next membership
                # but for others, we didn't expect a payment for this membership at the start
                vals = {"reference": self.reference, "paid": False}
                membership.write(vals)
            membership._mark_as_paid(amount_paid, move_id, bank_account_id)
            self.stored_reference = False
        return res

    def action_accept(self):
        status_obj = self.env["membership.state"]
        for partner in self:
            next_state = partner.simulate_next_state(event="accept")
            membership = self.env["membership.line"].search(
                [
                    ("id", "in", partner.membership_line_ids.ids),
                    ("active", "=", True),
                    (
                        "state_code",
                        "in",
                        ["former_member_committee", "member_committee"],
                    ),
                ],
                limit=1,
            )
            status = status_obj.search([("code", "=", next_state)], limit=1)
            if membership.state_id != status and membership:
                membership._close(force=True)
                membership.flush()
                w = self.env["add.membership"].create(
                    {
                        "int_instance_id": membership.int_instance_id.id,
                        "partner_id": partner.id,
                        "state_id": status.id,
                        "product_id": membership.product_id.id,
                    }
                )
                w.action_add()

    def action_refuse(self):
        status_obj = self.env["membership.state"]
        for partner in self:
            partner.accepted_date = False
            next_state = partner.simulate_next_state(event="refuse")
            membership = self.env["membership.line"].search(
                [
                    ("id", "in", partner.membership_line_ids.ids),
                    ("active", "=", True),
                    (
                        "state_code",
                        "in",
                        ["former_member_committee", "member_committee"],
                    ),
                ],
                limit=1,
            )
            status = status_obj.search([("code", "=", next_state)], limit=1)
            if membership.state_id != status and membership:
                membership._close(force=True)
                membership.flush()
                w = self.env["add.membership"].create(
                    {
                        "int_instance_id": membership.int_instance_id.id,
                        "partner_id": partner.id,
                        "state_id": status.id,
                        "product_id": membership.product_id.id,
                    }
                )
                w.action_add()
