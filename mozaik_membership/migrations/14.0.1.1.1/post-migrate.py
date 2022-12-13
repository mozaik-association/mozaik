# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Set value of boolean free_state on membership states defined in data")
    env = api.Environment(cr, SUPERUSER_ID, {})
    free_state_xml_ids = [
        "mozaik_membership.without_membership",
        "mozaik_membership.supporter",
        "mozaik_membership.former_supporter",
    ]

    state_ids = tuple([env.ref(xml_id).id for xml_id in free_state_xml_ids])

    cr.execute(
        """
        UPDATE membership_state
        SET free_state='t'
        WHERE id IN %(state_ids)s
        """,
        {"state_ids": state_ids},
    )
