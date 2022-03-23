# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Recompute address technical_name")
    env = api.Environment(cr, SUPERUSER_ID, {})
    technical_names = dict()
    for address in env["address.address"].search([]):
        address._compute_integral_address()
        if (address.technical_name, address.sequence) in technical_names:
            address.sequence = str(address.id)
        technical_names[(address.technical_name, address.sequence)] = address.id
