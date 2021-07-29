# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ProductTemplate(models.Model):

    _inherit = ['product.template']

    property_subscription_account = fields.Many2one(
        comodel_name='account.account', string='Subscription Account',
        company_dependent=True)
