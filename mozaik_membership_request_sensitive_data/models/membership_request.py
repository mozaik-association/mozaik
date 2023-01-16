# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models

from odoo.addons.mozaik_membership_request.models.membership_request import (
    EMPTY_ADDRESS,
)


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    @api.model
    def _get_sensitive_data(self):
        """
        Recover sensitive data from ir.config.parameter
        """
        sensitive_fields_str = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("membership.request.sensitive.fields")
        )
        if sensitive_fields_str == "[]":
            return []
        if (
            not sensitive_fields_str
            or sensitive_fields_str[0] != "["
            or sensitive_fields_str[-1] != "]"
        ):
            raise ValueError(_("Wrong format. Please encode a list of valid fields."))
        sensitive_fields_list = sensitive_fields_str[1:-1].split(",")
        sensitive_fields_list = [
            (field if len(field) < 2 or field[0] != " " else field[1:])
            for field in sensitive_fields_list
        ]  # Remove starting whitespaces
        return [field for field in sensitive_fields_list if field in self._fields]

    def _get_address_format_chatter_msg(self, partner_address):
        """
        Format msg to write in the membership request chatter, in case of an address
        change request.
        """
        self.ensure_one()
        address_mr = ""
        if self.address_local_street_id:
            address_mr += str(self.address_local_street_id.local_street) + ", "
        else:
            address_mr += (
                str(self.street_man or "No street")
                + ", "
                + str(self.street2 or "")
                + ", "
            )
        address_mr += (
            str(self.number or "No number") + ", " + str(self.box or "") + ", "
        )
        if self.city_man:
            address_mr += str(self.zip_man) + ", " + str(self.city_man) + ", "
        else:
            address_mr += (
                str(self.city_id.zipcode) + ", " + str(self.city_id.name) + ", "
            )
        address_mr += str(self.country_id.name or "No country")

        return (
            "\n "
            + "Address changed:"
            + str(partner_address.name)
            + " -> "
            + address_mr
            + "<br/>"
        )

    def _manage_sensitive_address_change(self):
        """
        When address is sensitive, some more work has to be done:
        address fields on the membership request and on the partner are not exactly
        the same, and we must compare them. We compute and make use of technical_name.
        """
        self.ensure_one()
        technical_name = self.technical_name or self.get_technical_name(
            self.address_local_street_id.id,
            self.city_id.id,
            self.number,
            self.box,
            self.city_man,
            self.street_man,
            self.zip_man,
            self.country_id.id,
        )
        partner_address = self.partner_id.address_address_id
        partner_technical_name = (
            partner_address.technical_name if partner_address else EMPTY_ADDRESS
        )
        res = {"chatter_msg_fields": "", "chg_values_update": {}}
        if (
            technical_name != EMPTY_ADDRESS
            and partner_technical_name != EMPTY_ADDRESS
            and technical_name != partner_technical_name
        ):
            # Avoid erasing address: remove address from membership
            chg_values_to_update = {
                "country_id": False,
                "address_local_street_id": False,
                "street_man": False,
                "street2": False,
                "number": False,
                "box": False,
                "city_man": False,
                "zip_man": False,
                "city_id": False,
                "technical_name": False,
            }
            res.update(
                {
                    "chatter_msg_fields": self._get_address_format_chatter_msg(
                        partner_address
                    ),
                    "chg_values_update": chg_values_to_update,
                }
            )
        return res

    def validate_request(self):
        """
        If partner was recognized, we check if sensitive data
        are different from the existing ones.
        """
        for mr in self:
            if not mr.partner_id:
                continue
            chatter_msg_fields = ""
            chg_values = {}
            sensitive_data = self._get_sensitive_data()
            if "technical_name" in sensitive_data:
                res = self._manage_sensitive_address_change()
                chatter_msg_fields += res["chatter_msg_fields"]
                chg_values.update(res["chg_values_update"])

            for key in [field for field in sensitive_data if field != "technical_name"]:
                mr_value = mr.mapped(key)[0]
                partner_value = mr.partner_id.mapped(key)[0]
                if partner_value and mr_value and partner_value != mr_value:
                    if key not in ["phone", "mobile"] or mr.get_format_phone_number(
                        partner_value
                    ) != mr.get_format_phone_number(mr_value):
                        # Just formatting phone/mobile number is
                        # not considered as a sensitive change
                        if (
                            key not in ["lastname", "firstname", "email"]
                            or mr_value.lower() != partner_value.lower()
                        ):
                            # Just changing lower/upper letters is not a sensitive change
                            chatter_msg_fields += (
                                "\n "
                                + key
                                + ": "
                                + str(partner_value)
                                + " -> "
                                + str(mr_value)
                                + "<br/>"
                            )
                            chg_values[key] = partner_value
            chatter_msg = (
                "Sensitive data not modified: <br/>"
                "&lt;field name&gt;: &lt;partner value&gt; -> "
                "&lt;membership value&gt; <br/> <br/>"
            )
            mr.write(chg_values)

            if chatter_msg_fields:
                mr._create_note(
                    "Sensitive data weren't modified", chatter_msg + chatter_msg_fields
                )
                # Create an activity for the user
                note = (
                    chatter_msg.replace("partner", "old").replace("membership", "new")
                    + chatter_msg_fields
                )
                mr.partner_id._schedule_activity(note, 5)

        return super().validate_request()
