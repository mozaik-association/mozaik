# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SurveyQuestionByDefault(models.Model):

    _name = "survey.question.by.default"
    _inherit = ["survey.question.by.default", "abstract.survey.question.type"]

    bridge_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Bridge field",
        default=False,
        help="The answer to this question will fill a field from the membership request.",
        ondelete="cascade",
    )

    @api.constrains("bridge_field_id")
    def _check_bridge_field_id(self):
        """
        1. bridge_field_id has to be a field from membership.request
        2. Two different questions by default cannot have the same bridge field.
        3. The type of field on bridge field has to correspond with the type of answer
           for the question to the survey. Example: if self.question_type == 'date'
           then self.bridge_field_id.ttype has to be equal to Date.
        """
        for question in self.filtered(lambda q: q.bridge_field_id):
            #  1.
            if question.bridge_field_id.model != "membership.request":
                raise ValidationError(
                    _("The field is not a field from model membership.request")
                )
            #  2.
            questions_by_default_with_bridge_field = self.env[
                "survey.question.by.default"
            ].search([("bridge_field_id", "!=", False), ("id", "!=", question.id)])
            used_bridge_field_ids = questions_by_default_with_bridge_field.mapped(
                "bridge_field_id"
            ).ids
            if question.bridge_field_id.id in used_bridge_field_ids:
                raise ValidationError(
                    _(
                        "Another question by default has the same "
                        "bridge field named %(bridge_field_name)s."
                    )
                    % {
                        "bridge_field_name": self.env["ir.model.fields"]
                        .browse(question.bridge_field_id.id)
                        .name
                    }
                )
            #  3.
            if question.question_type in self._get_dic().keys():
                expected_type_of_answer = self._get_expected_type_of_answer(question)
                if question.bridge_field_id.ttype not in expected_type_of_answer:
                    raise ValidationError(
                        _(
                            "The answer to this question will be of type "
                            "%(type_answer)s while the type of "
                            "the bridge field is %(type_bridge_field)s."
                        )
                        % {
                            "type_answer": expected_type_of_answer,
                            "type_bridge_field": question.bridge_field_id.ttype,
                        }
                    )
