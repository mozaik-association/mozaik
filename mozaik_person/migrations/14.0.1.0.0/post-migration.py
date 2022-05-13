import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Migrate res_partner identifier (Integer -> Char)")

    cr.execute(
        "UPDATE res_partner SET identifier = identifier_moved0",
    )

    _logger.info("Init is_address_duplicate_allowed from co_residency")

    cr.execute(
        """
        UPDATE res_partner
        SET is_address_duplicate_allowed_compute = true,
            is_address_duplicate_allowed = true
        WHERE co_residency_id IS NOT NULL
        """
    )
