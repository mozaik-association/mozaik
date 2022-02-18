# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    survey_user_input_id = fields.Many2one(
        comodel_name="survey.user_input",
        string="Associated Survey Answer",
        help="The membership request came from the answer to a survey.",
        readonly=True,
    )

    @api.depends("survey_user_input_id")
    def _compute_force_autoval(self):
        """
        If membership request is coming from answering to a survey,
        force_autoval equals the field force_autoval on the survey answer.
        """
        super()._compute_force_autoval()
        for record in self:
            if record.survey_user_input_id:
                record.force_autoval = record.survey_user_input_id.force_autoval

    def validate_request(self):
        """
        If the membership request is coming from a survey answer,
        then we associate the partner from the membership request
        to the survey answer.
        """
        super().validate_request()
        if (
            self.survey_user_input_id
            and self.state == "validate"
            and self.partner_id
            and not self.survey_user_input_id.partner_id
        ):
            self.survey_user_input_id.partner_id = self.partner_id
