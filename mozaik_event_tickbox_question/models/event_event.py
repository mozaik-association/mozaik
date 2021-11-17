# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EventEvent(models.Model):

    _inherit = "event.event"

    def _get_question_copy_values(self, question):
        res = super(EventEvent, self)._get_question_copy_values(question)
        res.update({"is_mandatory": question.is_mandatory})
        return res
