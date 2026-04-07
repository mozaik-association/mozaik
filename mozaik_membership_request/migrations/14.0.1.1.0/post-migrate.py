# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from psycopg2 import sql

_logger = logging.getLogger(__name__)

OLD_TABLE = "membership_request_involvement_category_rel"
NEW_TABLE = "membership_request_involvement"


def migrate(cr, version):
    if not version:
        return

    # Check that the old relation table exists
    cr.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = %s
        )
        """,
        (OLD_TABLE,),
    )
    if not cr.fetchone()[0]:
        _logger.info(
            "Old table %s not found, skipping migration.",
            OLD_TABLE,
        )
        return

    # Check that the new table exists (should have been created by ORM)
    cr.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = %s
        )
        """,
        (NEW_TABLE,),
    )
    if not cr.fetchone()[0]:
        _logger.error(
            "New table %s not found — cannot migrate data.",
            NEW_TABLE,
        )
        return

    # Safety: skip if data was already migrated
    cr.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(NEW_TABLE)))
    if cr.fetchone()[0] > 0:
        _logger.info(
            "Table %s already contains data, skipping migration.",
            NEW_TABLE,
        )
        return

    _logger.info(
        "Migrating data from %s to %s ...",
        OLD_TABLE,
        NEW_TABLE,
    )

    cr.execute(
        sql.SQL(
            """
            INSERT INTO {new}
                (membership_request_id, involvement_category_id,
                 create_uid, create_date, write_uid, write_date)
            SELECT
                rel.request_id,
                rel.category_id,
                1,
                NOW() AT TIME ZONE 'UTC',
                1,
                NOW() AT TIME ZONE 'UTC'
            FROM {old} rel
            """
        ).format(
            new=sql.Identifier(NEW_TABLE),
            old=sql.Identifier(OLD_TABLE),
        )
    )

    migrated_count = cr.rowcount
    _logger.info("Migrated %d records into %s.", migrated_count, NEW_TABLE)

    # Drop the old relation table — no longer needed
    cr.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(OLD_TABLE)))
    _logger.info("Dropped old table %s.", OLD_TABLE)
