# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    cr.execute("SELECT name FROM ir_module_module WHERE name='mozaik_mandate_email';")
    if cr.fetchall():
        _logger.info("Change mozaik_mandate_email module name")
        openupgrade.update_module_names(
            cr, [("mozaik_mandate_email", "mozaik_mandate_partner_fields")], True
        )
