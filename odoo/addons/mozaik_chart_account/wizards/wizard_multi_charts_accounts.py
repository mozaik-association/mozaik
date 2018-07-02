# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class WizardMultiChartsAccounts(models.TransientModel):

    _inherit = 'wizard.multi.charts.accounts'

    @api.model
    def _add_properties(
            self, chart_template_id, acc_template_ref, company_id, props):
        '''
        generate additional properties when deploying a charrt of accounts
        props: properties, list of tuples (field name, model, relation)
        '''
        field_obj = self.env['ir.model.fields']
        property_obj = self.env['ir.property']
        template = self.env['account.chart.template'].browse(
            [chart_template_id])
        for fld, model, relation in props:
            account = getattr(template, fld)
            value = account and \
                'account.account,' + str(acc_template_ref[account.id]) or \
                False
            if value:
                field = field_obj.search([
                    ('name', '=', fld),
                    ('model', '=', model),
                    ('relation', '=', relation),
                ], limit=1)
                vals = {
                    'name': fld,
                    'company_id': company_id,
                    'fields_id': field.id,
                    'value': value,
                }
                property_ids = property_obj.search(
                    [('name', '=', fld), ('company_id', '=', company_id)])
                if property_ids:
                    # the property exist: modify it
                    property_ids.write(vals)
                else:
                    # create the property
                    property_obj.create(vals)
