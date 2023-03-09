# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "Re-compute has_valid_mandate on all partners having an active banking mandate"
    )
    env = api.Environment(cr, SUPERUSER_ID, {})

    partners = (
        env["account.banking.mandate"]
        .search([("state", "=", "valid")])
        .mapped("partner_id")
    )
    partners._compute_has_valid_mandate()
