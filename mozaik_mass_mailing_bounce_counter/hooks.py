# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def post_init_hook(cr, registry):
    if openupgrade.table_exists(cr, "email_coordinate"):
        cr.execute(
            """
            UPDATE res_partner AS p
            SET email_bounced_date = e.bounce_date,
                first_email_bounced_date = e.first_bounce_date
            FROM email_coordinate AS e
            WHERE e.partner_id=p.id AND e.email=p.email
            """
        )
