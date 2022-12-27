import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "Recompute if partners are duplicates or not, "
        "for partners having an address without street"
    )
    env = api.Environment(cr, SUPERUSER_ID, {})

    partners = (
        env["res.partner"]
        .with_context(active_test=False)
        .search([("address_address_id", "!=", False)])
    )
    partners = partners.filtered(lambda p: not p.address_address_id.has_street)

    for partner in partners:
        _logger.info(
            "Processing partner ID:  %(partner_id)s (%(name)s)"
            % {"partner_id": partner.id, "name": partner.name}
        )
        values = [partner._get_discriminant_values()]
        partner._detect_and_repair_duplicate(values)
