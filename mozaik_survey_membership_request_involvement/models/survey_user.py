# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

UNKNOWN_PERSON = "Unknown person"


class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    membership_request_id = fields.One2many(
        comodel_name="membership.request",
        inverse_name="survey_user_input_id",
        string="Associated membership request",
    )
    force_autoval = fields.Boolean(
        string="Force auto-validation at creation",
        default=False,
        help="If a membership request is created when record is created, "
        "the membership request will be auto-validated.",
    )

    @api.model
    def create(self, vals):
        """
        At creation, we also create an empty membership_request.
        This mr will be updated with answers that contain a
        bridge field.
        NOTE: if partner_id is given, we set it with lastname,
        firstname and email.
        """
        values_mr = {"lastname": UNKNOWN_PERSON, "request_type": False}
        if "partner_id" in vals and vals["partner_id"]:
            partner = self.env["res.partner"].browse(vals["partner_id"])
            values_mr.update(
                {
                    "partner_id": partner.id,
                    "lastname": partner.lastname,
                    "firstname": partner.firstname or "",
                    "email": partner.email or "",
                }
            )
        mr = self.env["membership.request"].create(values_mr)
        user_input = super().create(vals)
        values_mr = {"survey_user_input_id": user_input.id}
        if user_input.survey_id.involvement_category_id:
            values_mr["involvement_category_ids"] = [
                (4, user_input.survey_id.involvement_category_id.id)
            ]
            values_mr["interest_ids"] = [
                (4, interest.id)
                for interest in user_input.survey_id.involvement_category_id.interest_ids
            ]
        mr.write(values_mr)
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
