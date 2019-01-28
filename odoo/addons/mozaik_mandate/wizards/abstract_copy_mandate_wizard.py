# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

WIZARD_AVAILABLE_ACTIONS = [
    ('renew', 'Renew Mandate'),
    ('add', 'Add Complementary Mandate'),
]


class AbstractCopyMandateWizard(models.TransientModel):

    _name = 'abstract.copy.mandate.wizard'

    _sql_constraints = [
        ('date_check', "CHECK(start_date <= deadline_date)",
         "The start date must be anterior to the deadline date."),
    ]

    _mandate_assembly_foreign_key = False

    mandate_category_id = fields.Many2one(
        comodel_name='mandate.category',
        string='Mandate Category',
        ondelete='cascade')
    new_mandate_category_id = fields.Many2one(
        comodel_name='mandate.category',
        string='Mandate Category',
        ondelete='cascade')
    mandate_id = fields.Many2one(
        comodel_name='abstract.mandate',
        string='Abstract Mandate',
        readonly=True,
        ondelete='cascade')
    assembly_id = fields.Many2one(
        comodel_name='abstract.assembly',
        string='Abstract Assembly',
        readonly=True,
        ondelete='cascade')
    new_assembly_id = fields.Many2one(
        comodel_name='abstract.assembly',
        string='Abstract Assembly',
        ondelete='cascade')
    instance_id = fields.Many2one(
        comodel_name='abstract.instance',
        string='Abstract Instance',
        ondelete='cascade')
    action = fields.Selection(
        selection=WIZARD_AVAILABLE_ACTIONS)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=True,
        ondelete='cascade')
    start_date = fields.Date()
    deadline_date = fields.Date()
    message = fields.Char()

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)
        context = self.env.context

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') or \
            (context.get('active_id') and
             [context.get('active_id')]) or \
            []

        for mandate in self.env[model].browse(ids):
            limit_date = mandate.end_date or mandate.deadline_date

            if limit_date > fields.Datetime.now():
                action = WIZARD_AVAILABLE_ACTIONS[1][0]
            else:
                action = WIZARD_AVAILABLE_ACTIONS[0][0]

            res['partner_id'] = mandate.partner_id.id
            res['mandate_category_id'] = mandate.mandate_category_id.id
            res['assembly_id'] = res['new_assembly_id'] \
                = mandate[self._mandate_assembly_foreign_key].id
            res['mandate_id'] = mandate.id
            res['instance_id'] = \
                mandate[self._mandate_assembly_foreign_key].instance_id.id
            if action == 'add':
                res['start_date'] = mandate.start_date
                res['deadline_date'] = mandate.deadline_date
            if action == 'renew':
                start_date = mandate.end_date if mandate.end_date \
                    else mandate.deadline_date
                start_date = (datetime.strptime(start_date,
                                                '%Y-%m-%d') +
                              relativedelta(days=1))
                res['start_date'] = start_date.strftime('%Y-%m-%d')
            res['action'] = action
            break

        return res

    @api.multi
    def renew_mandate(self):
        """
        ====================
        renew_mandate
        ====================
        Renew a mandate
        """
        self.ensure_one()
        vals = {
            'start_date': self.start_date,
            'deadline_date': self.deadline_date,
            'end_date': False,
        }
        return self._copy_mandate(vals)

    def add_mandate(self):
        """
        ===========
        add_mandate
        ===========
        Add a complementary mandate
        """
        values = dict(mandate_category_id=self.new_mandate_category_id.id,
                      start_date=self.start_date,
                      deadline_date=self.deadline_date)
        values[self._mandate_assembly_foreign_key] = self.new_assembly_id.id
        return self._copy_mandate(values)

    @api.multi
    def _copy_mandate(self, vals):
        """
        ===========
        copy_mandate
        ===========
        Copy a mandate with new default values
        """
        self.ensure_one()
        new_mandate_id = self.mandate_id.copy(default=vals)
        return new_mandate_id.get_formview_action()
