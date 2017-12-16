# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class MandateCategory(models.Model):

    _inherit = 'mandate.category'

    property_retrocession_account = fields.Many2one(
        comodel_name='account.account', string='Retrocession Account',
        company_dependent=True)
    property_retrocession_cost_account = fields.Many2one(
        comodel_name='account.account', string='Cost Account',
        company_dependent=True)
