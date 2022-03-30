# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.info("Delete user_bypass_security")
    cr.execute(
        """
        DELETE FROM ir_module_module
        WHERE name='user_bypass_security'
      """
    )
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE name = 'module_user_bypass_security'
        AND model = 'ir.module.module'
        AND module = 'base'
        """
    )
