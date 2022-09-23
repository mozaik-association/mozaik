# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    cr.execute("SELECT name FROM ir_module_module WHERE name='mozaik_mandate_email';")
    if cr.fetchall():
        _logger.info("Change mozaik_mandate_email module name")
        openupgrade.update_module_names(
            cr, [("mozaik_mandate_email", "mozaik_mandate_partner_fields")], True
        )

    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        env.ref("mozaik_mandate_partner_fields.group_mandate_see_email")
    except ValueError:
        return
    # If here, the old xmlid still exist.
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "mozaik_mandate_partner_fields.group_mandate_see_email",
                "mozaik_mandate_partner_fields.group_mandate_see_partner_fields",
            )
        ],
    )
