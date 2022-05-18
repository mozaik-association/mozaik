# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        """
        Remove membership_request_unique_ref constraint.
        """
    )
    cr.execute(
        "SELECT COUNT(*) "
        "FROM information_schema.table_constraints "
        "WHERE constraint_name='membership_request_unique_ref';"
    )
    res = cr.fetchone()[0]
    if res:
        cr.execute(
            "ALTER TABLE membership_request "
            "DROP CONSTRAINT membership_request_unique_ref;"
        )
