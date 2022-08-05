# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info(
        "Set value for previous_state_id on membership.lines, partner by partner"
    )
    _logger.info("--------- This may take several minutes -----------")
    env = api.Environment(cr, SUPERUSER_ID, {})

    counter = 0
    for partner in (
        env["res.partner"]
        .with_context(active_test=False)
        .search([("membership_line_ids", "!=", False)])
    ):
        counter += 1
        if counter % 500 == 0:
            _logger.info("----------------- Partners already reached: %s", counter)
        # First membership.line first
        sorted_lines = (
            env["membership.line"]
            .with_context(active_test=False)
            .search([("partner_id", "=", partner.id)], order="date_to, create_date")
        )
        previous_ml = sorted_lines[0]
        for ml in sorted_lines[1:]:
            ml.previous_state_id = previous_ml.state_id
            previous_ml = ml
