# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Sanitize address technical_name")
    env = api.Environment(cr, SUPERUSER_ID, {})
    for address in env["address.address"].search([]):
        address.write({"technical_name": str(address.id)})
