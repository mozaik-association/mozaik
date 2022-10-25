# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


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
            for key in self._get_sensitive_data():
                mr_value = mr.mapped(key)[0]
                partner_value = mr.partner_id.mapped(key)[0]
                if partner_value and mr_value and partner_value != mr_value:
                    if key not in ["phone", "mobile"] or mr.get_format_phone_number(
                        partner_value
                    ) != mr.get_format_phone_number(mr_value):
                        # Just formatting phone/mobile number is
                        # not considered as a sensitive change
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
