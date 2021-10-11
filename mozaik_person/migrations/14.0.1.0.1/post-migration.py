import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Recompute the related gender on partner (now in the oca addon)")

    cr.execute(
        "UPDATE res_partner SET gender = 'male' WHERE gender = 'm'",
    )
    cr.execute(
        "UPDATE res_partner SET gender = 'female' WHERE gender = 'f'",
    )
