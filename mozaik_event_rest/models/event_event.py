# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.http import request


class EventEvent(models.Model):

    _inherit = ["event.event"]

    image_url = fields.Char(string="Image URL", compute="_compute_image_url")
    is_headline = fields.Boolean(string="Headline")

    @api.depends("image")
    def _compute_image_url(self):
        host_url = request.httprequest.host_url
        for event in self:
            event.image_url = "%sweb/image_api/event.event/%d/image" % (
                host_url,
                event.id,
            )
