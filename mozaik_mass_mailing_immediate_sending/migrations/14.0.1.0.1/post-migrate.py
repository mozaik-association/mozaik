# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("'Email Marketing: process queue' cron set to run every 5 minutes.")
    cron_id = env.ref("mass_mailing.ir_cron_mass_mailing_queue").id
    query = """
    UPDATE ir_cron
    SET interval_number = 5
    WHERE id = %(id)s;
    """
    cr.execute(query, {"id": cron_id})
