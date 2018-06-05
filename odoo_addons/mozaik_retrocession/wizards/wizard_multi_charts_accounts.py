# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class WizardMultiChartsAccounts(models.TransientModel):

    _inherit = 'wizard.multi.charts.accounts'

    @api.model
    def generate_properties(
            self, chart_template_id, acc_template_ref, company_id):
        res = super(WizardMultiChartsAccounts, self).generate_properties(
            chart_template_id, acc_template_ref, company_id)

        props = [
            ('property_retrocession_account', 'mandate.category',
             'account.account'),
            ('property_retrocession_cost_account', 'mandate.category',
             'account.account'),
        ]

        self._add_properties(
            chart_template_id, acc_template_ref, company_id, props)

        return res
