# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.addons.mozaik_tools.tools import format_value
from odoo.fields import first

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
        tracking=True,
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
        default=lambda s: s._get_default_thesaurus_id(),
    )
    state = fields.Selection(
        selection=TERM_AVAILABLE_STATES,
        string='Status',
        readonly=True,
        required=True,
        tracking=True,
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

    @api.model
    def _get_default_thesaurus_id(self):
        return self.env['thesaurus'].search([], order='id desc', limit=1)

    def _track_subtype(self, init_values):
        record = first(self)
        if 'state' in init_values and record.state == 'draft':
            return 'mozaik_thesaurus.term_to_validate'
        return super(ThesaurusTerm, self)._track_subtype(init_values)

    @api.model
    def create(self, vals):
        """
        :param: vals
        :type: dictionary that contains at least 'name'
        """
        if not vals.get('search_name'):
            vals['search_name'] = vals.get('name')
        return super(ThesaurusTerm, self).create(vals)

    def write(self, vals):
        """
        :param: vals
        :type: dictionary
        """
        if not vals.get('search_name') and vals.get('name'):
            vals['search_name'] = vals['name']
        return super(ThesaurusTerm, self).write(vals)

    def _get_child_terms(self):
        """
        Returns all child terms of self recursively including self itself
        :return: terms recordSet
        """
        children = self.mapped('child_ids')
        terms = self.env[self._name]
        if children:
            terms |= children._get_child_terms()
        terms |= self
        return terms

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name and name[-1:] == '!':
            name = name[:-1]
            args += [
                '|',
                ('name', '=', name),
                ('select_name', '=', format_value(name, remove_blanks=True)),
            ]
        else:
            args += [
                '|',
                ('select_name', operator, name),
                ('search_name', operator, name),
            ]
        term_ids = self.search(args, limit=limit)
        return term_ids.name_get()

    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default.update({
            'name': _('%s (copy)') % self.name,
        })
        return super(ThesaurusTerm, self).copy(default=default)

    @api.model
    def _get_fields_to_update(self, mode):
        """
        Set state to cancel when invalidating a term
        :param mode: str
        :return: dict
        """
        result = super()._get_fields_to_update(mode)
        if mode == 'deactivate':
            result.update({
                'state': TERM_AVAILABLE_STATES[2][0],
            })
        if mode == 'activate':
            result.update({
                'state': TERM_AVAILABLE_STATES[0][0],
            })
        return result

    def button_confirm(self):
        """
        Confirm terms
        :rparam: True
        :rtype: boolean
        """
        vals = {
            'state': TERM_AVAILABLE_STATES[1][0]
        }
        return self.write(vals)

    def button_cancel(self):
        """
        Cancel terms
        :rparam: True
        :rtype: boolean
        """
        return self.action_invalidate()

    def button_reset(self):
        """
        Cancel the term
        :rparam: True
        :rtype: boolean
        """
        return self.action_revalidate()
