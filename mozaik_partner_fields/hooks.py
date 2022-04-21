# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Migrate partner birthdate")
    if openupgrade.column_exists(cr, "res_partner", "birth_date"):
        cr.execute(
            """
          UPDATE res_partner
          SET birthdate_date=birth_date
          """
        )


def post_init_hook(cr, registry):
    _logger.info("Migrate partner marital/civil status")
    if openupgrade.column_exists(cr, "res_partner", "civil_status"):
        openupgrade.map_values(
            cr,
            "civil_status",
            "marital",
            [
                ("s", "separated"),
                ("m", "married"),
                ("u", "unmarried"),
                ("w", "widower"),
                ("d", "divorced"),
            ],
            table="res_partner",
        )
