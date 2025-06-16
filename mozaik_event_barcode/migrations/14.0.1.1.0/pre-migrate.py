# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Add column 'is_voting_domain_required' on events")
    cr.execute(
        """
        ALTER TABLE event_event
        ADD COLUMN is_voting_domain_required BOOLEAN;
        """
    )
    _logger.info("Ticking 'is_voting_domain_required' if domain was set")
    cr.execute(
        """
        UPDATE event_event
        SET is_voting_domain_required = 't'
        WHERE voting_domain != '[]'
        """
    )
    _logger.info(
        "Untick 'can_vote' on registrations to events without required voting domain"
    )
    cr.execute(
        """
        UPDATE event_registration
        SET can_vote = 'f'
        WHERE event_id IN (
          SELECT id
          FROM event_event
          WHERE is_voting_domain_required != 't'
        )
        """
    )
