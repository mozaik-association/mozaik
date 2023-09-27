# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info(
        "Removing donation related features from mozaik_account. "
        "Going into mozaik_account_donation"
    )
    # Remove membership.line form view to reload the modified version
    openupgrade.logged_query(
        env.cr,
        """
        SELECT res_id
        FROM ir_model_data
        WHERE model='ir.ui.view'
        AND module='mozaik_account'
        AND name='membership_line_form_view'
        """,
    )
    res = env.cr.fetchone()
    if res:
        openupgrade.logged_query(
            env.cr,
            """
            DELETE FROM ir_ui_view
            WHERE id=%(res_id)s
            """,
            {"res_id": res[0]},
        )
