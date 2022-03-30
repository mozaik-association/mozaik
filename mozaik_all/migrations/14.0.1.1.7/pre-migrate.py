# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Uninstall user_bypass_security")
    cr.execute(
        """
      UPDATE ir_module_module
      SET state='to remove'
      WHERE name='user_bypass_security'
      """
    )
