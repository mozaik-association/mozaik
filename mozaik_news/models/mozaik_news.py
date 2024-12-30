# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MozaikNews(models.Model):

    _name = "mozaik.news"
    _description = "Mozaik News"
    _inherit = ["mozaik.privacy.domain.mixin"]

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date()
    content = fields.Html()
    image = fields.Binary()

    @api.constrains("start_date", "end_date")
    def _check_start_end_date(self):
        for rec in self:
            if rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError(
                    _("The end date cannot be earlier than the start date.")
                )
