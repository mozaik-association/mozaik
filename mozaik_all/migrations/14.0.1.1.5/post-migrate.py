# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    _logger.info("Delete mozaik_event_is_private and mozaik_survey_is_private modules")
    cr.execute(
        """
        DELETE FROM ir_module_module
        WHERE name='mozaik_event_is_private'
      """
    )
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE name = 'module_mozaik_event_is_private'
        AND model = 'ir.module.module'
        AND module = 'base'
        """
    )
    cr.execute(
        """
        DELETE FROM ir_module_module
        WHERE name='mozaik_survey_is_private'
      """
    )
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE name = 'module_mozaik_survey_is_private'
        AND model = 'ir.module.module'
        AND module = 'base'
        """
    )
