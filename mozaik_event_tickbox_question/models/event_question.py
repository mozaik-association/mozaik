# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EventQuestion(models.Model):

    _inherit = "event.question"
    question_type = fields.Selection(
        selection_add=[("tickbox", "Tickbox")],
        ondelete={"tickbox": "cascade"},
    )
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

    def action_view_question_answers(self):
        """Allow analyzing the attendees answers to petition questions
        in a convenient way:
        - A tree view showing checked tickboxes for tickbox questions."""

        action = super().action_view_question_answers()
        if self.question_type == "tickbox":
            action["views"] = [(False, "tree")]

        return action
