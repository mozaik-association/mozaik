# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
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
