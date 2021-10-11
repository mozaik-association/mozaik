import logging

from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Recompute the related gender on mandate")

    for table_name in ["sta_mandate", "ext_mandate", "int_mandate"]:
        cr.execute(
            "UPDATE %(table_name)s SET gender = 'male' WHERE gender = 'm'",
            {"table_name": AsIs(table_name)},
        )
        cr.execute(
            "UPDATE %(table_name)s SET gender = 'female' WHERE gender = 'f'",
            {"table_name": AsIs(table_name)},
        )
