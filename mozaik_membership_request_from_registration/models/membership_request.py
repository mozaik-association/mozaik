# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipRequest(models.Model):
    _inherit = "membership.request"

    def _find_input_partner(self, vals):
        """
        Find, if existing, the partner to add on the membership request,
        and update lastname, firstname and email, if not given.
        - If 'mr_partner_id' is a key of _context, then take the id given in the context
        to associate the partner id and DON'T USE partner_id given in vals.
        - If 'mr_partner_id' is not in the context, use field partner_id given in vals.
        """
        partner = False
        if "mr_partner_id" in self._context:
            mr_partner_id = self._context.get("mr_partner_id")
            if mr_partner_id:
                partner = self.env["res.partner"].browse(mr_partner_id)
        elif "partner_id" in vals and vals["partner_id"]:
            partner = self.env["res.partner"].browse(vals["partner_id"])

        if partner:
            if "lastname" not in vals or not vals["lastname"]:
                vals["lastname"] = partner.lastname
            if ("firstname" not in vals or not vals["firstname"]) and partner.firstname:
                vals["firstname"] = partner.firstname
            if "email" not in vals or not vals["email"]:
                vals["email"] = partner.email
        return partner

    @api.model
    def _pre_process_values(self, vals):
        """
        Pre-process values given in vals for creating the membership request.
        Returns a dictionary of values.
        """
        partner = self._find_input_partner(vals)
        values = {}
        if "lastname" in vals and vals["lastname"]:
            for key in ["lastname", "firstname"]:
                val = vals.get(key, False)
                if val:
                    vals[key] = val.strip().title()
            lastname = vals.get("lastname")
            firstname = vals.get("firstname", False)
            email = vals.get("email", False)
            phone = vals.get("phone", False)
            mobile = vals.get("mobile", False)
            country_id = vals.get("country_id", False)

            city_id = False
            zip_man = False
            # If zip is in vals: if it is recognized, we fill city_id
            if "city_id" in vals:
                city_id = vals["city_id"]
            elif "zip" in vals and vals["zip"]:
                candidate_city = self.env["res.city"].search(
                    [("zipcode", "=", vals["zip"])], limit=1
                )
                if candidate_city and (
                    not country_id or candidate_city.country_id.id == country_id
                ):
                    city_id = candidate_city.id
                else:
                    # In this case the zip was not automatically recognized,
                    # or the country of the zip does not correspond to country_id.
                    # Country is not set and zip is stored in zip_man.
                    country_id = False
                    zip_man = vals["zip"]
            else:
                country_id = False

            # If city_id, we now have to force the country
            if city_id and not country_id:
                country_id = self.env["res.city"].browse(city_id).country_id.id

            values = {}

            if city_id:
                # We do not want to get the default instance if
                # no city is given
                int_instance_id = self.get_int_instance_id(city_id)
                values["int_instance_ids"] = [(4, int_instance_id)]

            values.update(
                {
                    "lastname": lastname,
                    "firstname": firstname,
                    "email": email,
                    "phone": phone,
                    "mobile": mobile,
                    "is_company": False,
                    "request_type": False,
                    "country_id": country_id,
                    "city_id": city_id,
                    "zip_man": zip_man,
                    "effective_time": fields.datetime.now(),
                    "state": "confirm",
                }
            )

            # We know check all other keys from vals:
            # if the key is not in values and if it corresponds
            # to a field from membership.request, we add it to values
            for key in vals.keys():
                if (
                    key not in values
                    and key in self.env["membership.request"].fields_get()
                ):
                    values[key] = vals[key]

            # If a partner is given in vals, we do not change it
            if not partner:
                partner = self.get_partner_id(
                    is_company=False,
                    birthdate_date=False,
                    lastname=lastname,
                    firstname=firstname,
                    email=email,
                )
            values.update({"partner_id": partner.id if partner else False})
            # 26993/2.4.2.1.2
            # If the partner has no address but a membership state,
            # we force the instance to be the one of the partner.
            if partner and values["city_id"]:
                if not partner.address_address_id:
                    if partner.membership_state_id.code != "without_membership":
                        # 26993/2.4.2.1.2
                        values.update(
                            {"force_int_instance_id": partner.int_instance_ids[0].id}
                        )
                elif partner.address_address_id.city_id == values["city_id"]:
                    # 26993/2.4.2.2.1
                    values.update(
                        {
                            "country_id": False,
                            "city_id": False,
                            "force_int_instance_id": partner.int_instance_ids[0].id,
                        }
                    )
        return values

    def _create_membership_request(self, vals):
        values = self._pre_process_values(vals)
        if bool(values):
            request = self.with_context({"mode": "autoval"}).create(values)
            res = request._onchange_partner_id_vals(
                is_company=values["is_company"],
                request_type=values["request_type"],
                partner_id=values["partner_id"],
                technical_name=False,
            )
            request.write(res)
            return request
