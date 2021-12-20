# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

UNKNOWN_PERSON = "Unknown person"


class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    membership_request_id = fields.Many2one("membership.request")

    @api.model
    def create(self, vals):
        """
        At creation, we also create an empty membership_request.
        This mr will be updated with answers that contain a
        bridge field.
        """
        values_mr = {"lastname": UNKNOWN_PERSON, "request_type": False}
        mr = self.env["membership.request"].create(values_mr)
        vals.update({"membership_request_id": mr.id})
        user_input = super().create(vals)
        mr.write({"survey_user_input_id": user_input.id})
        return user_input


class SurveyUserInputLine(models.Model):

    _inherit = "survey.user_input.line"

    def _get_answer(self):
        """
        Returns the answer to the question, depending on the type of question
        """
        self.ensure_one()
        dic = {
            "char_box": self.value_char_box,
            "text_box": self.value_text_box,
            "numerical_box": self.value_numerical_box,
            "date": self.value_date,
            "datetime": self.value_datetime,
        }
        try:
            return dic[self.answer_type]
        except Exception as e:
            raise UserError(_("Invalid data")) from e
