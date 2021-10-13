# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class VirtualCustomPartner(models.Model):

    _name = "virtual.custom.partner"
    _inherit = ["virtual.master.partner"]
    _description = "Virtual Custom Partner"
    _auto = False

    def init(self):
        """
        Select all row of virtual.master.partner but take only main coordinate
        if there are
        """
        self.env.cr.execute(
            """
        create or replace view virtual_custom_partner as (
        SELECT
            *
        FROM
            virtual_master_partner

        WHERE (is_company IS TRUE or type = 'contact')
            )"""
        )
