# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE partner_involvement
        DROP CONSTRAINT IF EXISTS partner_involvement_multi_or_not;
        """,
    )
    # Next view was moved to mozaik_involvement_donation
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_model_data
        WHERE name='partner_involvement_donation_act_window'
        AND module='mozaik_involvement';
        """,
    )
