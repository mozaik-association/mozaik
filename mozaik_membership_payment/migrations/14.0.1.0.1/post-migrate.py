# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info(
        "Recompute latest_transaction, transaction_state and "
        "transaction_acquirer_id on active membership requests"
    )
    _logger.info("--------- This may take several minutes ---------")
    env["membership.request"].search([])._compute_latest_transaction()
