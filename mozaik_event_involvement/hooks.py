# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _create_involvement_category_event(cr):
    """
    We are looking in the DB for all events that do not have an associated
    involvement category and we are creating these involvement categories.
    """
    _logger.info("Creates an involvement category for each existing event.")
    env = api.Environment(cr, SUPERUSER_ID, {})
    event_ids_in_involvement_category = (
        env["partner.involvement.category"]
        .search([("event_id", "!=", False)])
        .mapped("event_id.id")
    )
    events_without_involvement_category = env["event.event"].search(
        [("id", "not in", event_ids_in_involvement_category)]
    )
    vals = []
    for event in events_without_involvement_category:
        vals += [
            {
                "name": event.name,
                "event_id": event.id,
                "involvement_type": "event",
                "allow_multi": True,
            }
        ]
    env["partner.involvement.category"].create(vals)


def post_init_hook(cr, registry):
    _create_involvement_category_event(cr)
