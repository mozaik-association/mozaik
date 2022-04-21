# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    _logger.info("Rename mandate fields is_submission_mandate, is_submission_assets")
    if openupgrade.column_exists(cr, "ext_mandate", "is_submission_mandate"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "ext.mandate",
                    "ext_mandate",
                    "is_submission_mandate",
                    "with_revenue_declaration",
                )
            ],
        )
    if openupgrade.column_exists(cr, "ext_mandate", "is_submission_assets"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "ext.mandate",
                    "ext_mandate",
                    "is_submission_assets",
                    "with_assets_declaration",
                )
            ],
        )
    if openupgrade.column_exists(cr, "int_mandate", "is_submission_mandate"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "int.mandate",
                    "int_mandate",
                    "is_submission_mandate",
                    "with_revenue_declaration",
                )
            ],
        )
    if openupgrade.column_exists(cr, "int_mandate", "is_submission_assets"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "int.mandate",
                    "int_mandate",
                    "is_submission_assets",
                    "with_assets_declaration",
                )
            ],
        )
    if openupgrade.column_exists(cr, "sta_mandate", "is_submission_mandate"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "sta.mandate",
                    "sta_mandate",
                    "is_submission_mandate",
                    "with_revenue_declaration",
                )
            ],
        )
    if openupgrade.column_exists(cr, "sta_mandate", "is_submission_assets"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "sta.mandate",
                    "sta_mandate",
                    "is_submission_assets",
                    "with_assets_declaration",
                )
            ],
        )
