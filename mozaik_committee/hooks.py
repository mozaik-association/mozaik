# Copyright 2021 ACSONE SA/NV
# License Other proprietary.

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Remove committee ir_config_prameters")
    cr.execute(
        """
      DELETE FROM ir_config_parameter
      WHERE key='sta_candidature_invalidation_delay'
      """
    )
    cr.execute(
        """
      DELETE FROM ir_config_parameter
      WHERE key='int_candidature_invalidation_delay'
      """
    )
    cr.execute(
        """
      DELETE FROM ir_config_parameter
      WHERE key='ext_candidature_invalidation_delay'
      """
    )
