# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FailureEditor(models.TransientModel):

    _name = 'failure.editor'
    _description = 'Failure Editor'

    increase = fields.Integer('Increase by', required=True, default=1)
    description = fields.Text('Description', required=True)
    model = fields.Char('Model', required=True)

    # constraints

    _sql_constraints = [
        ('increase_check',
         'CHECK(increase > 0)', '"increase" field should be a positive value'),
    ]

    # orm methods

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        if view_type == 'form':
            if not self.env.context.get('active_model', False):
                raise ValidationError(
                    _('Missing active_model in context!'))

            if not self.env.context.get('active_ids', False):
                raise ValidationError(
                    _('Missing active_ids in context!'))

            document_ids = self.env.context.get('active_ids')

            ids = self.env[self.env.context['active_model']].search(
                [('id', 'in', document_ids),
                 ('active', '=', False)])
            if ids:
                raise ValidationError(
                    _('This action is not allowed on inactive documents!'))

        res = super().fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        return res

    # public methods

    @api.multi
    def update_failure_datas(self):
        """
        ===================
        update_failure_datas
        ===================
        Update the failure information of coordinate.
        ``ids`` of the coordinate is contained into the active_ids of the
        context.
        """
        res_ids = self.env.context.get('active_ids', False)
        if not res_ids:
            return
        for wiz in self:
            vals = {
                'failure_description': wiz.description,
                'failure_date': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            }
            coordinates = self.env[wiz.model].browse(res_ids)
            for coordinate in coordinates:
                failure_counter = coordinate.failure_counter
                vals.update({
                    'failure_counter': failure_counter + wiz.increase,
                })
                coordinate.write(vals)
