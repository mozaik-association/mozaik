# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Pre-create and populate stored computed columns via SQL.

    Without this hook, the ORM computes partner_id row-by-row in Python
    for every mailing.trace record, accumulating results in RAM before
    flushing. On large databases (millions of traces), this leads to
    hours-long hangs and eventual OOM crashes.
    """
    # Check if there's any data worth pre-filling
    cr.execute("SELECT EXISTS (SELECT 1 FROM mailing_trace LIMIT 1)")
    if not cr.fetchone()[0]:
        _logger.info(
            "mozaik_mass_mailing_partner: mailing_trace is empty, "
            "nothing to pre-fill."
        )
        return

    cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'mailing_trace'
          AND column_name IN (
              'partner_id', 'is_received', 'is_opened', 'is_clicked'
          )
        """
    )
    existing = {row[0] for row in cr.fetchall()}

    if len(existing) == 4:
        _logger.info(
            "mozaik_mass_mailing_partner: all columns already exist, "
            "skipping pre-fill (module already installed or re-upgrade)."
        )
        return

    cr.execute("SELECT COUNT(*) FROM mailing_trace")
    count = cr.fetchone()[0]
    _logger.info(
        "mozaik_mass_mailing_partner: pre-filling %d mailing traces via SQL.",
        count,
    )

    if "is_received" not in existing:
        _logger.info("Pre-creating and filling mailing_trace.is_received")
        cr.execute("ALTER TABLE mailing_trace ADD COLUMN is_received BOOLEAN")
        cr.execute(
            "UPDATE mailing_trace "
            "SET is_received = (sent IS NOT NULL AND exception IS NULL)"
        )

    if "is_opened" not in existing:
        _logger.info("Pre-creating and filling mailing_trace.is_opened")
        cr.execute("ALTER TABLE mailing_trace ADD COLUMN is_opened BOOLEAN")
        cr.execute("UPDATE mailing_trace SET is_opened = (opened IS NOT NULL)")

    if "is_clicked" not in existing:
        _logger.info("Pre-creating and filling mailing_trace.is_clicked")
        cr.execute("ALTER TABLE mailing_trace ADD COLUMN is_clicked BOOLEAN")
        cr.execute("UPDATE mailing_trace SET is_clicked = (clicked IS NOT NULL)")

    if "partner_id" not in existing:
        _logger.info("Pre-creating and filling mailing_trace.partner_id")
        cr.execute("ALTER TABLE mailing_trace ADD COLUMN partner_id INTEGER")
        cr.execute(
            """
            UPDATE mailing_trace
            SET partner_id = res_id
            WHERE model = 'res.partner'
              AND res_id IS NOT NULL
              AND EXISTS (
                  SELECT 1
                  FROM res_partner rp
                  WHERE rp.id = mailing_trace.res_id
              )
            """
        )
        cr.execute(
            "CREATE INDEX IF NOT EXISTS mailing_trace_partner_id_index "
            "ON mailing_trace (partner_id)"
        )

    _logger.info("mozaik_mass_mailing_partner: pre-init hook complete.")
