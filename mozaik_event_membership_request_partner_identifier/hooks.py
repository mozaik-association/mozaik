# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _recompute_partner_identifier(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env["event.registration"].with_context(active_test=False).search(
            []
        )._compute_partner_identifier()


def post_init_hook(cr, registry):
    """
    Addon mozaik_event_registration_partner_identifier defines the partner_identifier
    field on event registrations.
    This addon override the compute method to take care of the associated_partner_id field.
    Hence the hook computing the value on all records must be done in this module.
    """
    _logger.info("Fill partner_identifier on event registrations")
    _recompute_partner_identifier(cr)
