# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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

    def adding_new_question_to_event(self):
        res = super().adding_new_question_to_event()
        res["is_mandatory"] = self.is_mandatory
        return res

    def action_view_question_answers(self):
        """Allow analyzing the attendees answers to petition questions
        in a convenient way:
        - A tree view showing checked tickboxes for tickbox questions."""

        action = super().action_view_question_answers()
        if self.question_type == "tickbox":
            action["views"] = [(False, "tree")]

        return action
