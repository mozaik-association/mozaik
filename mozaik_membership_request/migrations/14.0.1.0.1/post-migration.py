import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Update the gender on membership.request")

    cr.execute(
        "UPDATE membership_request SET gender = 'male' WHERE gender = 'm'",
    )
    cr.execute(
        "UPDATE membership_request SET gender = 'female' WHERE gender = 'f'",
    )
