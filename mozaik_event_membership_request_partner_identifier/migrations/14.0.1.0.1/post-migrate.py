# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.mozaik_event_membership_request_partner_identifier.hooks import (
    _recompute_partner_identifier,
)

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Compute partner_identifier on existing event registrations")
    _recompute_partner_identifier(cr)
