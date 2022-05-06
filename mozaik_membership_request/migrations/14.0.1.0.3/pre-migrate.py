# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    _logger.info(
        "Copy columns 'local_voluntary', 'regional_voluntary', "
        "'national_voluntary', 'local_only'"
    )
    column_names = [
        "local_voluntary",
        "regional_voluntary",
        "national_voluntary",
        "local_only",
    ]
    column_spec = []
    for column_name in column_names:
        if not openupgrade.column_exists(
            cr, "membership_request", column_name + "_old"
        ):
            column_spec += [(column_name, column_name + "_old", None)]
    openupgrade.copy_columns(
        cr,
        {"membership_request": column_spec},
    )
