import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Migrate res_partner identifier (Integer -> Char)")

    cr.execute(
        "UPDATE res_partner SET identifier = identifier_moved0",
    )
