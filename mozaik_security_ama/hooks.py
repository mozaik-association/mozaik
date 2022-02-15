# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _set_int_instance_ids(cr):
    _logger.info("Set int_instance_ids on AMA objets")
    env = api.Environment(cr, SUPERUSER_ID, {})
    if openupgrade.column_exists(cr, "event_event", "int_instance_id"):
        openupgrade.m2o_to_x2m(
            cr, env["event.event"], "event_event", "int_instance_ids", "int_instance_id"
        )
    if openupgrade.column_exists(cr, "petition_petition", "int_instance_id"):
        openupgrade.m2o_to_x2m(
            cr,
            env["petition.petition"],
            "petition_petition",
            "int_instance_ids",
            "int_instance_id",
        )
    if openupgrade.column_exists(cr, "survey_survey", "int_instance_id"):
        openupgrade.m2o_to_x2m(
            cr,
            env["survey.survey"],
            "survey_survey",
            "int_instance_ids",
            "int_instance_id",
        )


def post_init_hook(cr, registry):
    _set_int_instance_ids(cr)
