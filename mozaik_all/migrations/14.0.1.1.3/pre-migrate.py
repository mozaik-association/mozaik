# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "Changing mail templates (on res.partner) parameter 'use_default_to' from False to True"
    )

    templates = env["mail.template"].search([("model_id.model", "=", "res.partner")])
    templates.write({"use_default_to": True})
