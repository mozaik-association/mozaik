# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "'Include opt-out contacts set to False if mass mailing model "
        "is not Contact or Distribution List."
    )

    env = api.Environment(cr, SUPERUSER_ID, {})
    ids = (
        env["ir.model"]
        .search(
            ["|", ("model", "=", "distribution.list"), ("model", "=", "res.partner")]
        )
        .mapped("id")
    )

    query = """
        UPDATE mailing_mailing
        SET include_opt_out_contacts=false
        WHERE mailing_model_id NOT IN %s
    """
    cr.execute(query, (tuple(ids),))
