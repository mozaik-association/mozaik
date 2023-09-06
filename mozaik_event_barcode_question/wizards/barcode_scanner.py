# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BarcodeScanner(models.TransientModel):

    _inherit = "barcode.scanner"

    registration_answers = fields.Html(compute="_compute_registration_answers")

    def _get_square_tickbox_question(self, value):
        if value:
            return "<p><span>&#x2611;</span></p>"
        return "<p><span>&#x25A2;</span></p>"

    @api.depends("event_registration_id")
    def _compute_registration_answers(self):
        for wiz in self:
            msg = ""
            for (
                reg_answer
            ) in wiz.event_registration_id.registration_answer_ids.filtered(
                lambda r: r.question_id.must_appear_at_scanning
            ):
                msg += f"<p> <b> {reg_answer.question_id.title} </b> </p>"
                if reg_answer.question_type == "simple_choice":
                    msg += f"<p> {reg_answer.value_answer_id.name} </p>"
                elif reg_answer.question_type == "text_box":
                    msg += f"<p> {reg_answer.value_text_box} </p>"
                elif reg_answer.question_type == "tickbox":
                    msg += self._get_square_tickbox_question(reg_answer.value_tickbox)
            wiz.registration_answers = msg
