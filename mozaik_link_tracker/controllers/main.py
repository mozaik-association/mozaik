# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import werkzeug

from odoo import http
from odoo.http import request

from odoo.addons.mass_mailing.controllers.main import MassMailController

_logger = logging.getLogger(__name__)


class MozaikLinkTracker(MassMailController):
    @http.route("/r/<string:code>/m/<int:mailing_trace_id>", type="http", auth="public")
    def full_url_redirect(self, code, mailing_trace_id, **post):
        country_code = request.session.get(
            "geoip", False
        ) and request.session.geoip.get("country_code", False)

        _logger.info(
            "request.httprequest.environ dict: %s" % request.httprequest.environ
        )

        request.env["link.tracker.click"].sudo().add_click(
            code,
            ip=request.httprequest.remote_addr,
            country_code=country_code,
            mailing_trace_id=mailing_trace_id,
        )
        return werkzeug.utils.redirect(
            request.env["link.tracker"].get_url_from_code(code), 301
        )
