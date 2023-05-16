# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Set value of boolean free_state on former members")
    env = api.Environment(cr, SUPERUSER_ID, {})
    state_id = env.ref("mozaik_membership.former_member").id

    cr.execute(
        """
        UPDATE membership_state
        SET free_state='t'
        WHERE id = %(state_id)s
        """,
        {"state_id": state_id},
    )
