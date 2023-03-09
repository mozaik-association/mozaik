# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(
        "Payment returns: rename active_membership_line_id to to_process_membership_line_id"
    )
    cr = env.cr
    openupgrade.rename_columns(
        cr,
        {
            "payment_return": [
                ("active_membership_line_id", "to_process_membership_line_id")
            ]
        },
    )
