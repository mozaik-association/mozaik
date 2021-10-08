# -*- encoding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Recompute the related gender on mandate")

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for model_name in ['sta.mandate', 'ext.mandate', 'int.mandate']:
            model = env[model_name]
            env.add_to_compute(model._fields['gender'], model.search([]))
            model.recompute()
