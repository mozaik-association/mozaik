# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    _logger.info("Setting email_bounced = 0 if Null")
    cr.execute(
        """
        UPDATE res_partner
        SET email_bounced = 0
        WHERE email_bounced IS NULL;
    """
    )

    _logger.info("Uninstall mozaik_event_is_private and mozaik_survey_is_private")
    cr.execute(
        """
        UPDATE ir_module_module
        SET state='to remove'
        WHERE name='mozaik_event_is_private'
    """
    )
    cr.execute(
        """
        UPDATE ir_module_module
        SET state='to remove'
        WHERE name='mozaik_survey_is_private'
    """
    )

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        try:
            res_group = env.ref("mozaik_survey_is_private.group_survey_child_instances")
            res_group.unlink()
        except ValueError:
            _logger.info("Res group survey: user limited already deleted.")

    _logger.info("Rename column int_instance_id on AMA objects")
    if openupgrade.column_exists(cr, "event_event", "int_instance_id"):
        openupgrade.rename_columns(
            {"event_event": [("int_instance_id", "int_instance_id_old")]}
        )
    if openupgrade.column_exists(cr, "petition_petition", "int_instance_id"):
        openupgrade.rename_columns(
            {"petition_petition": [("int_instance_id", "int_instance_id_old")]}
        )
    if openupgrade.column_exists(cr, "petition_petition", "int_instance_id"):
        openupgrade.rename_columns(
            {"survey_survey": [("int_instance_id", "int_instance_id_old")]}
        )
