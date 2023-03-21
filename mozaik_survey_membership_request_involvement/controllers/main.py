# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http

from odoo.addons.survey.controllers.main import Survey


class SurveyMembershipRequest(Survey):
    @http.route(
        "/survey/submit/<string:survey_token>/<string:answer_token>",
        type="json",
        auth="public",
        website=True,
    )
    def survey_submit(self, survey_token, answer_token, **post):
        response = super().survey_submit(survey_token, answer_token, **post)

        access_data = self._get_access_data(
            survey_token, answer_token, ensure_token=True
        )
        if access_data["validity_code"] is not True:
            return {"error": access_data["validity_code"]}
        answer_sudo = access_data["answer_sudo"]

        # Fill and validate the MR only if we reached the last question/page.
        if answer_sudo.state == "done":
            self._fill_membership_request(answer_sudo)

        return response

    def _fill_membership_request(self, answer_sudo):
        """
        Looks at bridge fields to fill the membership request.
        Adds involvements categories on membership request.
        """
        membership_request = answer_sudo.membership_request_id
        values = {}  # will contain all answers to bridge fields
        for user_input_line in answer_sudo.user_input_line_ids.filtered(
            lambda uil: not uil.skipped and uil.question_id.bridge_field_id
        ):
            answer = user_input_line._get_answer()
            values.update({user_input_line.question_id.bridge_field_id.name: answer})

        # If no lastname is given in the bridge field, either the partner_id was
        # specified, or we are still with UNKNOWN_PERSON
        # In both cases we want to update the membership request, so we fill "lastname"
        values["lastname"] = (
            values.pop("lastname", False) or membership_request.lastname
        )

        values = membership_request._pre_process(values)
        membership_request.write(values)

        res = membership_request._onchange_partner_id_vals(
            is_company=values.get("is_company", False),
            request_type=values.get("request_type", False),
            partner_id=values.get("partner_id", False),
            technical_name=False,
        )
        membership_request.write(res)

        # Adding involvement categories
        command_ic = []
        command_interests = []
        for answer in answer_sudo.user_input_line_ids.mapped(
            "suggested_answer_id"
        ).filtered(lambda s: s and s.involvement_category_id):
            command_ic += [(4, answer.involvement_category_id.id)]
            command_interests += [
                (4, interest.id)
                for interest in answer.involvement_category_id.interest_ids
            ]
        membership_request.write(
            {"involvement_category_ids": command_ic, "interest_ids": command_interests}
        )
        membership_request._auto_validate_may_be_forced(
            answer_sudo.survey_id.auto_accept_membership
        )
