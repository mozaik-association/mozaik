# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Remove distribution_list email composer view")
    cr.execute(
        """
        DELETE FROM ir_ui_view WHERE id IN
        (
            SELECT res_id FROM ir_model_data
            WHERE name='email_compose_message_wizard_form'
            AND module='distribution_list'
        )
      """
    )
