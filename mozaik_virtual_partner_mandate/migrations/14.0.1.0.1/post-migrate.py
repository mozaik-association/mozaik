# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.info(
        "Modify distribution list line templates "
        "applied to Partner/Mandate: add ['active_mandate', '=', True]"
    )

    cr.execute(
        """
     UPDATE distribution_list_line_template
     SET domain_handwritten =
      CONCAT('[["active_mandate", "=", True], ', right(domain_handwritten, -1))
     WHERE
         src_model_id = (SELECT id FROM ir_model WHERE model='virtual.partner.mandate')
         AND manually_edit_domain='t';
    """
    )

    cr.execute(
        """
     UPDATE distribution_list_line_template
     SET domain_widget = CONCAT('[["active_mandate", "=", True], ', right(domain_widget, -1))
     WHERE
         src_model_id = (SELECT id FROM ir_model WHERE model='virtual.partner.mandate')
         AND (manually_edit_domain='f' OR manually_edit_domain IS NULL);
    """
    )
