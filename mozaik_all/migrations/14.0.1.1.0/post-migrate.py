# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Init candidature statechart")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for ext_candidature in env["ext.candidature"].search([]):
            ext_candidature.sc_state = json.dumps(
                {"configuration": ["root", ext_candidature.state]}
            )
        for int_candidature in env["int.candidature"].search([]):
            int_candidature.sc_state = json.dumps(
                {"configuration": ["root", int_candidature.state]}
            )
        for sta_candidature in env["sta.candidature"].search([]):
            sta_candidature.sc_state = json.dumps(
                {"configuration": ["root", sta_candidature.state]}
            )
