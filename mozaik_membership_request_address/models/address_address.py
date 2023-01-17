# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AddressAddress(models.Model):

    _inherit = "address.address"

    def _delete_unused_addresses(self):
        """
        Delete all addresses not linked to a partner and not
        linked to a membership request that is in state 'draft' or 'confirm'.
        We use a SQL query to speed up the execution
        """
        query = """
        DELETE FROM address_address WHERE id IN  (
          SELECT ad.id
          FROM address_address ad
          WHERE NOT EXISTS(
            SELECT id
            FROM res_partner
            WHERE address_address_id = ad.id
          ) AND NOT EXISTS(
            SELECT id
            FROM membership_request
            WHERE address_id = ad.id AND state IN ('draft', 'confirm')
          )
        );"""
        self.env.cr.execute(query)
