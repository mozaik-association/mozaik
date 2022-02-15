# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for address in env["address.address"].search(
        [("address_local_street_id", "!=", False)]
    ):
        address.street_man = address.address_local_street_id.local_street
