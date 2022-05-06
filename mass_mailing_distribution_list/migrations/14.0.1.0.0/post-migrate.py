# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Init mailing_model_id distribution_list")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        distribution_list_model = env["ir.model"].search(
            [("model", "=", "distribution.list")]
        )
        env["mailing.mailing"].search([("distribution_list_id", "!=", False)]).write(
            {"mailing_model_id": distribution_list_model.id}
        )
