# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Recompute address technical_name")
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["address.address"].search([])._compute_integral_address()
