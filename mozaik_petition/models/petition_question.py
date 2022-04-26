# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PetitionQuestion(models.Model):

    _name = "petition.question"
    _description = "Petition Question"
    _order = "sequence,id"
    _rec_name = "title"

    title = fields.Char(required=True, translate=True)
    question_type = fields.Selection(
        [
            ("simple_choice", "Selection"),
            ("text_box", "Text Input"),
            ("tickbox", "Tickbox"),
        ],
        default="simple_choice",
        string="Question Type",
        required=True,
    )

    petition_id = fields.Many2one("petition.petition", "Petition", ondelete="cascade")
    petition_type_id = fields.Many2one("petition.type", string="Petition Template")
    answer_ids = fields.One2many(
        "petition.question.answer", "question_id", "Answers", copy=True
    )
    sequence = fields.Integer(default=10)
    is_mandatory = fields.Boolean(
        string="Is Mandatory",
        help="If True, the signatory has to check "
        "the box to continue the registration.",
        default=False,
    )

    @api.onchange("question_type")
    def _onchange_question_type(self):
        """
        For non tickbox questions, we want 'is mandatory' field
        to be False
        """
        self.ensure_one()
        if self.question_type != "tickbox":
            self.is_mandatory = False

    def name_get(self):
        res = []
        for record in self:
            display_name = "%s" % (record.title)
            res.append((record.id, display_name))
        return res

    def write(self, vals):
        """We add a check to prevent changing the question_type
        of a question that already has answers.
        Indeed, it would mess up the petition.registration.answer
        (answer type not matching the question type)."""

        if "question_type" in vals:
            questions_new_type = self.filtered(
                lambda question: question.question_type != vals["question_type"]
            )
            if questions_new_type:
                answer_count = self.env["petition.registration.answer"].search_count(
                    [("question_id", "in", questions_new_type.ids)]
                )
                if answer_count > 0:
                    raise UserError(
                        _(
                            "You cannot change the question type "
                            "of a question that already has answers!"
                        )
                    )
        return super().write(vals)

    def action_view_question_answers(self):
        """Allow analyzing the attendees answers to petition questions
        in a convenient way:
        - A graph view showing counts of each suggestions for simple_choice questions
          (Along with secondary pivot and tree views)
        - A tree view showing textual answers values for text_box questions.
        - A tree view showing textual answers values for tickbox questions."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mozaik_petition.action_petition_registration_report"
        )
        action["domain"] = [("question_id", "=", self.id)]
        if self.question_type == "simple_choice":
            action["views"] = [(False, "graph"), (False, "pivot"), (False, "tree")]
        elif self.question_type in ["text_box", "tickbox"]:
            action["views"] = [(False, "tree")]
        return action


class PetitionQuestionAnswer(models.Model):
    """Contains suggested answers to a 'simple_choice' petition.question."""

    _name = "petition.question.answer"
    _order = "sequence,id"
    _description = "Petition Question Answer"

    name = fields.Char("Answer", required=True, translate=True)
    question_id = fields.Many2one(
        "petition.question", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
