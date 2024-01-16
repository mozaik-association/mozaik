# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import werkzeug

from odoo import api, fields, models
from odoo.http import request


class SurveySurvey(models.Model):

    _inherit = ["survey.survey"]

    image_url = fields.Char(string="Image URL", compute="_compute_image_url")
    permanent_link = fields.Char(
        string="Permanent Link", compute="_compute_permanent_link"
    )

    @api.depends("background_image")
    def _compute_image_url(self):
        host_url = request.httprequest.host_url
        for survey in self:
            survey.image_url = "%sweb/image_api/survey.survey/%d/background_image" % (
                host_url,
                survey.id,
            )

    @api.depends("access_token")
    def _compute_permanent_link(self):
        for survey in self:
            survey.permanent_link = werkzeug.urls.url_join(
                survey.get_base_url(), survey.get_start_url()
            )
