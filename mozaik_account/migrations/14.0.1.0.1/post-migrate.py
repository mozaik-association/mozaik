# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.info(
        "Free membership lines without a regularization date:"
        "set the creation date as regularization date."
    )
    cr.execute(
        """
        UPDATE membership_line
        SET regularization_date = create_date
        WHERE regularization_date IS NULL AND paid='t' AND price_paid IS NULL;
        """
    )

    _logger.info(
        "Paid membership lines without a regularization date:"
        "set the date of the account.move as regularization date."
    )
    cr.execute(
        """
        UPDATE membership_line ml
        SET regularization_date=am.date
        FROM account_move am
        WHERE ml.move_id=am.id
          AND ml.regularization_date IS NULL
          AND paid='t'
          AND price_paid > 0
          AND move_id IS NOT NULL;
        """
    )
