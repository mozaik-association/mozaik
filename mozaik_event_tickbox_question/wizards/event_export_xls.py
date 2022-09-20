# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EventExportXls(models.TransientModel):

    _inherit = "event.export.xls"

    def _compute_answer(self, lines):
        """
        Add the case of a tickbox question
        """
        answer = super()._compute_answer(lines)
        if len(lines) == 1 and lines.question_type == "tickbox":
            answer = lines.value_tickbox
        return answer
