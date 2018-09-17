# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, tools


class MembershipLine(models.Model):
    _inherit = 'membership.line'

    account_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Account move",
        readonly=True,
    )
    
    @api.model
    @tools.ormcache('reference')
    def _get_membership_line_by_ref(self, reference):
        """
        Get a membership.line based on given reference.
        As the reference is unique, we can put the result in cache to avoid
        multi-search
        :param reference: str
        :return: self recordset
        """
        domain = [
            ('reference', '=', reference),
        ]
        return self.search(domain, limit=1)

    @api.model
    @tools.ormcache('reference')
    def _get_product_by_ref(self, reference):
        """
        Get a product from the line related to the given reference
        As the reference is unique, we can put the result in cache to avoid
        multi-search
        :param reference: str
        :return: self recordset
        """
        return self._get_membership_line_by_ref(reference).product_id
