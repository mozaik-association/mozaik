# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PartnerInvolvement(models.Model):

    _inherit = "partner.involvement"

    question_event_id = fields.Many2one(
        "event.question",
        string="Corresponding question",
        help="This involvement has a link with a question asked at an event subscription.",
        readonly=True,
    )

    def _get_on_list(self):
        return super()._get_on_list() + ["question_event_id"]

    @api.constrains("question_event_id", "involvement_category_id")
    def _check_question_event_id(self):
        for record in self:
            if record.question_event_id and record.involvement_type != "event":
                raise ValidationError(
                    _(
                        "You cannot enter a question_event_id if "
                        "the involvement_type is not 'event'."
                    )
                )
