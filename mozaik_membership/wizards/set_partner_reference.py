# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.fields import first


class SetPartnerReference(models.TransientModel):

    _name = "set.partner.reference"
    _description = "Set the reference to the selected partner"

    def doit(self):
        membership_object = self.env["membership.line"]
        context = self.env.context
        active_model = context.get("active_model")
        active_ids = context.get("active_ids")
        if active_model == "res.partner" and active_ids:
            target_obj = self.env[active_model]
            partners = target_obj.browse(active_ids)
            for partner in partners:
                partner.stored_reference = (
                    membership_object._generate_membership_reference(
                        partner,
                        first(partner.int_instance_ids),
                    )
                )
