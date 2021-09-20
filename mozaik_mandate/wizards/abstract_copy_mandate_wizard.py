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
        related='mandate_id.mandate_category_id',
        readonly=True)
    new_mandate_category_id = fields.Many2one(
        comodel_name='mandate.category',
        string='Mandate Category')
    mandate_id = fields.Many2one(
        comodel_name='abstract.mandate',
        string='Abstract Mandate',
        readonly=True)
    assembly_id = fields.Many2one(
        comodel_name='abstract.assembly',
        string='Abstract Assembly',
        readonly=True)
    new_assembly_id = fields.Many2one(
        comodel_name='abstract.assembly',
        string='Abstract Assembly')
    instance_id = fields.Many2one(
        related="assembly_id.instance_id",
        readonly=True)
    action = fields.Selection(
        selection=WIZARD_AVAILABLE_ACTIONS)
    partner_id = fields.Many2one(
        related="mandate_id.partner_id",
        string='Partner',
        readonly=True)
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

            # res['mandate_category_id'] = mandate.mandate_category_id.id TODO
            res['assembly_id'] = res['new_assembly_id'] \
                = mandate[self._mandate_assembly_foreign_key].id
            res['mandate_id'] = mandate.id
            if action == 'add':
                res['start_date'] = mandate.start_date
                res['deadline_date'] = mandate.deadline_date
            else:
                start_date = mandate.end_date if mandate.end_date \
                    else mandate.deadline_date
                start_date = (datetime.strptime(start_date,
                                                '%Y-%m-%d') +
                              relativedelta(days=1))
                res['start_date'] = start_date.strftime('%Y-%m-%d')
            res['action'] = action
            break

        return res

    def renew_mandate(self):
        """
        Renew a mandate
        """
        self.ensure_one()
        vals = self._renew_mandate_vals()
        return self._copy_mandate(vals)

    def _renew_mandate_vals(self):
        self.ensure_one()
        return {
            'start_date': self.start_date,
            'deadline_date': self.deadline_date,
            'end_date': False,
        }

    def add_mandate(self):
        """
        Add a complementary mandate
        """
        self.ensure_one()
        values = self._add_mandate_vals()
        return self._copy_mandate(values)

    def _add_mandate_vals(self):
        self.ensure_one()
        return {
            "mandate_category_id": self.new_mandate_category_id.id,
            "start_date": self.start_date,
            "deadline_date": self.deadline_date,
            self._mandate_assembly_foreign_key: self.new_assembly_id.id,
        }

    def _copy_mandate(self, vals):
        """
        Copy a mandate with new default values
        """
        self.ensure_one()
        # copy() reset lang, thus form will be displayed in en_US
        new_mandate_id = self.mandate_id.copy(
            default=vals).with_context(lang=self._context.get('lang'))
        return new_mandate_id.get_formview_action()

    @api.onchange("new_mandate_category_id")
    def _onchange_new_mandate_category_id(self):
        for wiz in self:
            wiz.new_assembly_id = False
