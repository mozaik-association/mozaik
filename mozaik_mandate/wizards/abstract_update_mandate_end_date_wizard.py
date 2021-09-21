# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AbstractUpdateMandateEndDateWizard(models.TransientModel):

    _name = 'abstract.update.mandate.end.date.wizard'
    _description = 'Abstract Update Mandate End Date Wizard'

    mandate_end_date = fields.Date()
    mandate_deadline_date = fields.Date()
    mandate_id = fields.Many2one(
        comodel_name='abstract.mandate',
        string='Mandate',
        readonly=True)
    message = fields.Char(
        readonly=True)

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)
        context = self.env.context

        mode = context.get('mode', 'end_date')

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        mandate = self.env[model].browse(ids[0])
        res['mandate_id'] = mandate.id

        if mode == 'end_date':
            res['mandate_end_date'] = fields.Date.today()

            if mandate.active:
                res['message'] = _('Mandate will be invalidated'
                                   ' by setting its end date!')
        elif mode == 'reactivate':
            if mandate.active:
                res['message'] = _(
                    'The selected mandate is already active!')
            if not mandate.mandate_category_id.active:
                res['message'] = _('The mandate category is no longer active!')
            if mandate.designation_int_assembly_id and \
                    not mandate.designation_int_assembly_id.active:
                res['message'] = _('The designation assembly '
                                   'is no longer active!')
            if not mandate.partner_id.active:
                res['message'] = _('The representative is no longer active!')
        return res

    def set_mandate_end_date(self):
        self.ensure_one()
        if self.mandate_end_date > fields.Date.today():
            raise ValidationError(
                _('End date must be lower or equal than today!'))
        if self.mandate_end_date > self.mandate_id.deadline_date:
            raise ValidationError(
                _('End date must be lower or equal than deadline date!'))
        if self.mandate_id.start_date > self.mandate_end_date:
            raise ValidationError(
                _('End date must be greater or equal than start date!'))
        vals = {'end_date': self.mandate_end_date}
        if self.mandate_id.active:
            self.mandate_id.action_invalidate(vals=vals)
        else:
            self.mandate_id.write(vals=vals)

    def reactivate_mandate(self):
        self.ensure_one()
        if self.mandate_deadline_date <= fields.Date.today():
            raise ValidationError(
                _('New deadline date must be greater than today !'))

        vals = {
            'deadline_date': self.mandate_deadline_date,
            'end_date': False,
        }
        self.mandate_id.action_revalidate(vals=vals)
