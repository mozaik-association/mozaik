# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        """
        Change local_voluntary, regional_voluntary,
        national_voluntary, local_only booleans into select fields:
        boolean false -> force_false ; boolean true -> force_true.
        """
    )
    field_names = [
        "local_voluntary",
        "regional_voluntary",
        "national_voluntary",
        "local_only",
    ]
    query = """
      UPDATE membership_request
      SET %(field_name)s='%(force_value)s'
      WHERE %(old_field_name)s = %(value)s;
      """
    for field_name in field_names:
        cr.execute(
            query,
            {
                "old_field_name": AsIs(field_name + "_old"),
                "field_name": AsIs(field_name),
                "force_value": AsIs("force_true"),
                "value": AsIs("true"),
            },
        )
        cr.execute(
            query,
            {
                "old_field_name": AsIs(field_name + "_old"),
                "field_name": AsIs(field_name),
                "force_value": AsIs("force_false"),
                "value": AsIs("false"),
            },
        )
