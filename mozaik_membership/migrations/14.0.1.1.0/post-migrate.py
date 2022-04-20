# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(
        "Rename table res_partner_int_instance_rel "
        "=> res_partner_int_instance_manager"
    )
    cr = env.cr
    if openupgrade.table_exists(cr, "res_partner_int_instance_rel"):
        cr.execute("DROP TABLE IF EXISTS res_partner_int_instance_manager")
        openupgrade.rename_tables(
            cr, [("res_partner_int_instance_rel", "res_partner_int_instance_manager")]
        )
