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
        DELETE FROM ir_ui_view
        WHERE name='partner.involvement.search (mozaik_membership)'
        OR name='partner.involvement.tree (mozaik_membership)';
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_model_data
        WHERE (name='partner_involvement_search_view'
          OR name='partner_involvement_tree_view')
        AND module='mozaik_membership';
        """,
    )
