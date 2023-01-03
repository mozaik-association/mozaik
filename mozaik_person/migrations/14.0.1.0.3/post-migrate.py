import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "Partners that have a partial address "
        "cannot be flagged as duplicates on basis of their address"
    )
    env = api.Environment(cr, SUPERUSER_ID, {})

    addresses = env["address.address"].search([("has_street", "=", False)])

    for address in addresses.filtered(lambda a: len(a.partner_ids) > 1):
        partners = address.partner_ids
        _logger.info(
            "Cleaning duplicates of partial address "
            "ID %(address_id)s (%(address_name)s) for partners %(partner_ids)s"
            % {
                "address_id": address.id,
                "address_name": address.name,
                "partner_ids": partners.ids,
            }
        )
        values_write = env["res.partner"]._get_fields_to_update_duplicate(
            "reset", "address_address_id"
        )
        partners.with_context(escape_detection=True).write(values_write)
