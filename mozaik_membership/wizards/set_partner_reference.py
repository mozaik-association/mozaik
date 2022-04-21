# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import first


class SetPartnerReference(models.TransientModel):

    _name = "set.partner.reference"
    _description = "Set the reference to the selected partner"

    have_wrong_status_partner = fields.Boolean()

    @api.model
    def default_get(self, fields_list):
        result = super(SetPartnerReference, self).default_get(fields_list)

        context = self.env.context
        active_model = context.get("active_model")
        active_ids = context.get("active_ids")
        result["have_wrong_status_partner"] = True
        if active_model == "res.partner" and active_ids:
            target_obj = self.env[active_model]
            partner_count = target_obj.search_count(
                [
                    ("id", "in", active_ids),
                    ("membership_state_id", "in", self._get_available_state().ids),
                ]
            )
            if partner_count == len(active_ids):
                result["have_wrong_status_partner"] = False
        return result

    @api.model
    def _get_available_state(self):
        return self.env["membership.state"].search(
            [
                (
                    "code",
                    "in",
                    ("supporter", "former_member"),
                )
            ]
        )

    def doit(self):
        membership_object = self.env["membership.line"]
        context = self.env.context
        active_model = context.get("active_model")
        active_ids = context.get("active_ids")
        if active_model == "res.partner" and active_ids:
            target_obj = self.env[active_model]
            partners = target_obj.search(
                [
                    ("id", "in", active_ids),
                    ("membership_state_id", "in", self._get_available_state().ids),
                ]
            )
            for partner in partners:
                partner.stored_reference = (
                    membership_object._generate_membership_reference(
                        partner,
                        first(partner.int_instance_ids),
                    )
                )
