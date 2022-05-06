# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Mig bounce counters")
    cr = env.cr
    if openupgrade.table_exists(cr, "email_coordinate"):
        cr.execute(
            """
            UPDATE res_partner AS p
            SET email_bounced = e.bounce_counter,
                email_bounced_description = e.bounce_description
            FROM email_coordinate AS e
            WHERE e.partner_id=p.id AND e.email=p.email
            """
        )
    if openupgrade.table_exists(cr, "postal_coordinate"):
        cr.execute(
            """
            UPDATE res_partner AS p
            SET last_postal_failure_date = pc.bounce_date,
                postal_bounced = true
            FROM postal_coordinate AS pc
            WHERE pc.partner_id=p.id AND pc.is_main=true AND pc.bounce_date IS NOT NULL
            """
        )
