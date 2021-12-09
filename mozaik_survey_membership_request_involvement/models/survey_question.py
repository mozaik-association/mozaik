# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SurveyQuestion(models.Model):

    _name = "survey.question"
    _inherit = ["survey.question", "abstract.survey.question.type"]

    bridge_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Bridge field",
        default=False,
        help="The answer to this question will fill a field from the membership request.",
        ondelete="cascade",
    )

    @api.onchange("bridge_field_id")
    def _onchange_bridge_field_id(self):
        """
        1. Raises an error if the bridge field has already been chosen in another question
           of the survey.
        2. The type of field on bridge field has to correspond with the type of answer
           for the question to the survey. Example: if self.question_type == 'date'
           then self.bridge_field_id.ttype has to be equal to Date. Raises an error
           if this is not the case.
        """
        if self.bridge_field_id:
            #  1.
            questions_with_bridge_field = self.survey_id.question_and_page_ids.filtered(
                lambda q: q.bridge_field_id
            )
            used_bridge_field_ids = questions_with_bridge_field.mapped(
                "bridge_field_id"
            ).ids
            # Since the record was maybe not created yet, ids can be new ids.
            # Hence we cannot use .ids
            questions_with_bridge_field_ids = questions_with_bridge_field.mapped("id")
            new_question_id = self.id
            if (
                self.bridge_field_id
                and self.bridge_field_id.id in used_bridge_field_ids
                and new_question_id not in questions_with_bridge_field_ids
            ):
                raise ValidationError(
                    _(
                        "Another question by default has the same "
                        "bridge field named %(bridge_field_name)s."
                    )
                    % {
                        "bridge_field_name": self.env["ir.model.fields"]
                        .browse(self.bridge_field_id.id)
                        .name
                    }
                )
            #  2.
            if self.question_type in self._get_dic().keys():
                expected_type_of_answer = self._get_expected_type_of_answer(self)
                if self.bridge_field_id.ttype not in expected_type_of_answer:
                    raise ValidationError(
                        _(
                            "The answer to this question will be of type "
                            "%(type_answer)s while the type of "
                            "the bridge field is %(type_bridge_field)s."
                        )
                        % {
                            "type_answer": expected_type_of_answer,
                            "type_bridge_field": self.bridge_field_id.ttype,
                        }
                    )
