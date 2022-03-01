# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.column_exists(cr, "distribution_list", "int_instance_id_old"):
        openupgrade.m2o_to_x2m(
            cr,
            env["distribution.list"],
            "distribution_list",
            "int_instance_ids",
            "int_instance_id_old",
        )
