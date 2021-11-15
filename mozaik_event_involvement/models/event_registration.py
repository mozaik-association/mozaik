# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class EventRegistration(models.Model):

    _inherit = "event.registration"

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._create_membership_request_from_registration(vals)
        return rec

    def _create_membership_request_from_registration(self, vals):
        self.ensure_one()
        request = self._create_membership_request(vals)

        if request.partner_id and self.event_id.auto_accept_membership:
            request.validate_request()

    def _create_membership_request(self, vals):
        model_mr = self.env["membership.request"]
        if "lastname" in vals and vals["lastname"]:
            lastname = vals["lastname"]
            firstname = vals["firstname"] if "firstname" in vals else False
            email = vals["email"] if "email" in vals else False
            phone = vals["phone"] if "phone" in vals else False
            int_instance = self.event_id.int_instance_id
            values = {
                "lastname": lastname,
                "firstname": firstname,
                "email": email,
                "phone": phone,
                "is_company": False,
                "request_type": "s",
                "int_instance_ids": [(4, int_instance.id)],
            }

            partner = model_mr.get_partner_id(
                is_company=False,
                birthdate_date=False,
                lastname=lastname,
                firstname=firstname,
                email=email,
            )

            values.update({"partner_id": partner.id if partner else False})
            request = model_mr.create(values)
            res = request._onchange_partner_id_vals(
                is_company=values["is_company"],
                request_type=values["request_type"],
                partner_id=values["partner_id"],
                technical_name=False,
            )
            request.write(res)
