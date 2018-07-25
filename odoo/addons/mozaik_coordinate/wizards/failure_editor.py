# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FailureEditor(models.TransientModel):
    _name = 'failure.editor'
    _description = 'Failure Editor'

    increase = fields.Integer(
        'Increase by',
        required=True,
        default=1)
    description = fields.Text(
        required=True,
    )
    model = fields.Char(
        required=True,
    )

    _sql_constraints = [
        ('increase_check',
         'CHECK(increase > 0)', '"increase" field should be a positive value'),
    ]

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        context = self.env.context
        if view_type == 'form':
            active_model = context.get('active_model', False)
            active_ids = context.get('active_ids', [])
            if not active_model:
                raise UserError(_('Missing active_model in context!'))

            if not active_ids:
                raise UserError(_('Missing active_ids in context!'))
            domain = [
                ('id', 'in', active_ids),
                ('active', '=', False),
            ]
            if self.env[active_model].search_count(domain):
                raise UserError(
                    _('This action is not allowed on inactive documents!'))
        return super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)

    @api.multi
    def update_failure_datas(self):
        """
        Update the failure information of coordinate.
        ``ids`` of the coordinate is contained into the active_ids of the
        context.
        :return: {}
        """
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', False)
        if not active_ids:
            return {}
        vals = {
            'failure_description': self.description,
            'failure_date': fields.Datetime.now(),
        }
        coordinates = self.env[self.model].browse(active_ids)
        for coordinate in coordinates:
            vals.update({
                'failure_counter': coordinate.failure_counter + self.increase,
            })
            coordinate.write(vals)
        return {}
