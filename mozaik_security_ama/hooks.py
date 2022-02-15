# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _set_int_instance_ids(cr):
    _logger.info("Set int_instance_ids on AMA objets")
    if openupgrade.column_exists(cr, "event_event", "int_instance_id"):
        openupgrade.m2o_to_x2m(
            cr, "event.event", "event_event", "int_instance_ids", "int_instance_id"
        )
    if openupgrade.column_exists(cr, "petition_petition", "int_instance_id"):
        openupgrade.m2o_to_x2m(
            cr,
            "petition.petition",
            "petition_petition",
            "int_instance_ids",
            "int_instance_id",
        )
    if openupgrade.column_exists(cr, "survey_survey", "int_instance_id"):
        openupgrade.m2o_to_x2m(
            cr,
            "survey.survey",
            "survey_survey",
            "int_instance_ids",
            "int_instance_id",
        )


def pre_init_hook(cr):
    _set_int_instance_ids(cr)
