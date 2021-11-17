# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Candidatures 'suggested' to 'designated'")
    cr.execute(
        """
        UPDATE ext_candidature
        SET state = 'designated'
        WHERE state = 'suggested';
    """
    )
    cr.execute(
        """
        UPDATE int_candidature
        SET state = 'designated'
        WHERE state = 'suggested';
    """
    )
    cr.execute(
        """
        UPDATE sta_candidature
        SET state = 'designated'
        WHERE state = 'suggested';
    """
    )
