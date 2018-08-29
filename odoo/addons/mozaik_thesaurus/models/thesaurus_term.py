# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.osv import expression
from odoo.addons.mozaik.tools import format_value

# Available States for thesaurus terms
TERM_AVAILABLE_STATES = [
    ('draft', 'Unconfirmed'),
    ('confirm', 'Confirmed'),
    ('cancel', 'Cancelled'),
]


class ThesaurusTerm(models.Model):

    _name = 'thesaurus.term'
    _inherit = ['mozaik.abstract.model']
    _description = 'Thesaurus Term'
    _order = 'search_name'
    _unicity_keys = 'name'
    _rec_name = 'search_name'

    @api.multi
    @api.depends('search_name')
    def _compute_select_name(self):
        for record in self:
            record.select_name = format_value(
                record.search_name,
                remove_blanks=True)

    name = fields.Char(
        string='Term',
        required=True,
        index=True,
        track_visibility='onchange',
    )
    search_name = fields.Char(
        string='Term (Full Path)',
        index=True,
        readonly=True,
    )
    select_name = fields.Char(
        compute='_compute_select_name',
        store=True,
        index=True,
    )
    thesaurus_id = fields.Many2one(
        comodel_name='thesaurus',
        string='Thesaurus',
        required=True,
    )
    state = fields.Selection(
        selection=TERM_AVAILABLE_STATES,
        string='Status',
        readonly=True,
        required=True,
        track_visibility='onchange',
        default=TERM_AVAILABLE_STATES[0][0],
        copy=False,
    )
    parent_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        relation='child_term_parent_term_rel',
        column1='child_term_id',
        column2='parent_term_id',
        string='Parent Terms',
        copy=False,
    )
    child_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        relation='child_term_parent_term_rel',
        column1='parent_term_id',
        column2='child_term_id',
        string='Child Terms',
        copy=False,
    )

    @api.multi
    def _track_subtype(self, init_values):
        record = self[0]
        if 'state' in init_values and record.state == 'draft':
            return 'mozaik_thesaurus.term_to_validate'
        return super(ThesaurusTerm, self)._track_subtype(init_values)

    @api.model
    def create(self, vals):
        """
        :param: vals
        :type: dictionary that contains at least 'name'
        :rparam: id of the new term
        :rtype: integer
        """
        if not vals.get('search_name'):
            vals['search_name'] = vals.get('name')
        return super(ThesaurusTerm, self).create(vals)

    @api.multi
    def _get_child_terms(self):
        children = self.mapped('child_ids')
        terms = self.env[self._name]
        if children:
            terms |= children._get_child_terms()
        terms |= self
        return terms

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if len(name) and name[-1:] == '!':
            name = name[:-1]
            args += [
                '|',
                ('name', '=', name),
                ('select_name', '=', name),
            ]
        else:
            args += [
                '|',
                 ('select_name', operator, name),
                 ('search_name', operator, name),
            ]
        term_ids = super(ThesaurusTerm, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        return term_ids.name_get()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default.update({
            'name': _('%s (copy)') % self.name,
        })
        return super(ThesaurusTerm, self).copy(default=default)

    @api.multi
    def button_confirm(self):
        """
        Confirm the term
        :rparam: True
        :rtype: boolean
        """
        vals = {
            'state': TERM_AVAILABLE_STATES[1][0]
        }
        self.write(vals)

    @api.multi
    def button_cancel(self):
        """
        Cancel the term
        :rparam: True
        :rtype: boolean
        Note:
        Reset the notification term to avoid the expected exception related to
        an active reference
        """
        self.ensure_one()
        # Reset notification term on the thesaurus
        self.thesaurus_id.update_notification_term()
        return super(ThesaurusTerm, self).action_invalidate(
            vals={'state': TERM_AVAILABLE_STATES[2][0]})

    @api.multi
    def button_reset(self):
        """
        Cancel the term
        :rparam: True
        :rtype: boolean
        """
        self.ensure_one()
        return super(ThesaurusTerm, self).action_revalidate(
            vals={'state': TERM_AVAILABLE_STATES[0][0]})
