# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.info(
        "Free membership lines without a regularization date: "
        "set the creation date as regularization date."
    )
    cr.execute(
        """
        UPDATE membership_line
        SET regularization_date = create_date
        WHERE regularization_date IS NULL AND paid='t' AND price_paid IS NULL;
        """
    )
