# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.column_exists(cr, "membership_request", "int_instance_id"):
        openupgrade.rename_columns(
            cr, {"membership_request": [("int_instance_id", "int_instance_id_old")]}
        )
