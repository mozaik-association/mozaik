# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    def _compute_scoring_values(self):
        """
        Re-compute the score if we asked to ignore skipped questions.
        """
        super()._compute_scoring_values()
        for user_input in self:
            if user_input.survey_id.exclude_not_answered_from_total:
                # Questions that were answered
                questions_to_count = user_input.user_input_line_ids.filtered(
                    lambda q: not q.skipped
                ).mapped("question_id")
                total_possible_score = 0

                for question in questions_to_count:
                    if question.question_type == "simple_choice":
                        total_possible_score += max(
                            (
                                score
                                for score in question.mapped(
                                    "suggested_answer_ids.answer_score"
                                )
                                if score > 0
                            ),
                            default=0,
                        )
                    elif question.question_type == "multiple_choice":
                        total_possible_score += sum(
                            score
                            for score in question.mapped(
                                "suggested_answer_ids.answer_score"
                            )
                            if score > 0
                        )
                    elif question.is_scored_question:
                        total_possible_score += question.answer_score

                if total_possible_score == 0:
                    # If he skipped all scored questions: we let him have 100%
                    user_input.scoring_total = 0
                    user_input.scoring_percentage = 100

                else:
                    score_total = sum(
                        user_input.user_input_line_ids.filtered(
                            lambda q: not q.skipped
                        ).mapped("answer_score")
                    )
                    user_input.scoring_total = score_total
                    score_percentage = (score_total / total_possible_score) * 100
                    user_input.scoring_percentage = (
                        round(score_percentage, 2) if score_percentage > 0 else 0
                    )
