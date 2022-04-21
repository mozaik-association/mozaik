# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    _logger.info(
        "Rename table ext_mandate_term_competencies_rel "
        "=> ext_mandate_thesaurus_term_rel"
    )
    if openupgrade.table_exists(cr, "ext_mandate_term_competencies_rel"):
        cr.execute("DROP TABLE IF EXISTS ext_mandate_thesaurus_term_rel")
        openupgrade.rename_tables(
            cr,
            [("ext_mandate_term_competencies_rel", "ext_mandate_thesaurus_term_rel")],
        )
    _logger.info(
        "Rename table sta_mandate_term_competencies_rel "
        "=> sta_mandate_thesaurus_term_rel"
    )
    if openupgrade.table_exists(cr, "sta_mandate_term_competencies_rel"):
        cr.execute("DROP TABLE IF EXISTS sta_mandate_thesaurus_term_rel")
        openupgrade.rename_tables(
            cr,
            [("sta_mandate_term_competencies_rel", "sta_mandate_thesaurus_term_rel")],
        )
