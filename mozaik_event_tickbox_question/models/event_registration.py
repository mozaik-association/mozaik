# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventRegistrationAnswer(models.Model):

    _inherit = "event.registration.answer"
    is_mandatory = fields.Boolean(related="question_id.is_mandatory")
    value_tickbox = fields.Boolean(string="Checked", default=False)

    _sql_constraints = [
        (
            "value_check",
            "CHECK(value_tickbox IS NOT NULL OR "
            "value_answer_id IS NOT NULL OR "
            "COALESCE(value_text_box, '') <> '')",
            "There must be a suggested value or a text value.",
        )
    ]

    @api.constrains("value_tickbox")
    def _check_value_tickbox(self):
        for record in self:
            if record.is_mandatory and not record.value_tickbox:
                raise ValidationError(
                    _("At least one mandatory tickbox is not checked.")
                )
