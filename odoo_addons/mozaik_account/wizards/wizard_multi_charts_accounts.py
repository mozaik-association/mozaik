# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _


class WizardMultiChartsAccounts(models.TransientModel):

    _inherit = 'wizard.multi.charts.accounts'

    @api.model
    def generate_properties(
            self, chart_template_id, acc_template_ref, company_id):
        res = super(WizardMultiChartsAccounts, self).generate_properties(
            chart_template_id, acc_template_ref, company_id)

        props = [
            ('property_subscription_account', 'product.template',
             'account.account'),
        ]

        self._add_properties(
            chart_template_id, acc_template_ref, company_id, props)

        self._prepare_operation_templates(chart_template_id, acc_template_ref)

        return res

    def _prepare_operation_templates(
            self, chart_template_id, acc_template_ref):
        template = self.env['account.chart.template'].browse(
            [chart_template_id])
        account = getattr(template, 'property_subscription_account')
        account_id = account and account.id or False
        vals = {
            'name': _('Subscriptions'),
            'account_id': account_id and
            acc_template_ref[account_id] or False,
            'label': _('Subscriptions'),
            'amount_type': 'percentage_of_total',
            'amount': 100.0,
        }
        self.env['account.statement.operation.template'].create(vals)
