# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Setting email_bounced = 0 if Null")
    cr.execute(
        """
        UPDATE res_partner
        SET email_bounced = 0
        WHERE email_bounced IS NULL;
    """
    )
