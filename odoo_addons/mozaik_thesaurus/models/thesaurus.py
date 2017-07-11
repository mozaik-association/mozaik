# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_thesaurus, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_thesaurus is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_thesaurus is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_thesaurus.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, api, fields
from openerp.tools.translate import _
from openerp.addons.mozaik_base.base_tools import format_value


# Available States for thesaurus terms
TERM_AVAILABLE_STATES = [
    ('draft', 'Unconfirmed'),
    ('confirm', 'Confirmed'),
    ('cancel', 'Cancelled'),
]

term_available_states = dict(TERM_AVAILABLE_STATES)


class Thesaurus(models.Model):

    _name = 'thesaurus'
    _inherit = ['mozaik.abstract.model']
    _description = 'Thesaurus'
    _order = 'name'

    _track = {
        'new_thesaurus_term_id': {
            'mozaik_thesaurus.mt_thesaurus_add_term':
                lambda self, cr, uid, obj, ctx=None: obj.new_thesaurus_term_id,
        },
    }

    name = fields.Char('Thesaurus', required=True, track_visibility='onchange')
    new_thesaurus_term_id = fields.Many2one(
        comodel_name='thesaurus.term', string='New Term to Validate',
        readonly=True, track_visibility='onchange')

    _unicity_keys = 'name'

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if not self.env.context('copy_allowed'):
            raise Warning(_('A Thesaurus cannot be duplicated!'))

    @api.multi
    def update_notification_term(self, newid=False):
        """
        Update the field new_thesaurus_term_id producing or not a notification
        """
        vals = {'new_thesaurus_term_id': newid}
        if not newid:
            # notrack=Tue: disable tracking notification when
            # resetting new term id
            self.with_context(mail_notrack=True).write(vals)
        else:
            self.write(vals)


class ThesaurusTerm(models.Model):

    _name = 'thesaurus.term'
    _inherit = ['mozaik.abstract.model']
    _description = 'Thesaurus Term'
    _order = 'search_name'
    _unicity_keys = 'name'
    _rec_name = 'search_name'

    @api.model
    def _get_default_thesaurus_id(self):
        return self.env['thesaurus'].search([], limit=1).id

    @api.one
    @api.constrains('ext_identifier', 'state')
    def _check_ext_identifier(self):
        """
        :raise Warning: if ext_identifier is not set when validating term
        """
        if self.state == 'confirm' and not self.ext_identifier:
            raise Warning(
                _('Missing External Identifier for a validated term'))

    @api.multi
    def _compute_search_name(self):
        self.ensure_one()
        name_path = self.name
        names = [self.name]
        parent_ids = self.parent_m2m_ids._ids
        while parent_ids:
            for p_id in parent_ids:
                parent = self.browse(p_id)
                if parent.name not in names:
                    names.append(parent.name)
                parent_ids += parent.parent_m2m_ids._ids
                parent_ids = filter(lambda a: a != p_id, parent_ids)
        if names:
            names.reverse()
            name_path = '/'.join(names)
        return name_path

    @api.one
    def compute_search_name(self):
        if self.parent_m2m_ids:
            self.search_name = self._compute_search_name()
        else:
            self.search_name = self.name

    @api.one
    @api.depends('search_name')
    def _compute_select_name(self):
        self.select_name = format_value(self.search_name, remove_blanks=True)

    name = fields.Char(
        string='Term', required=True, index=True, track_visibility='onchange')
    search_name = fields.Char(
        string='Term (Full Path)', index=True, readonly=True)
    select_name = fields.Char(
        compute='_compute_select_name', store=True, index=True)
    thesaurus_id = fields.Many2one(
        comodel_name='thesaurus', string='Thesaurus', readonly=True,
        required=True, default=_get_default_thesaurus_id)
    ext_identifier = fields.Char(
        string='External Identifier', required=False, index=True,
        track_visibility='onchange', states={'confirm': [('required', True)]},
        copy=False)
    state = fields.Selection(
        selection=TERM_AVAILABLE_STATES, string='Status', readonly=True,
        required=True, track_visibility='onchange',
        default=TERM_AVAILABLE_STATES[0][0], copy=False)
    parent_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term', relation='child_term_parent_term_rel',
        column1='child_term_id', column2='parent_term_id',
        string='Parent Terms', copy=False)
    children_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term', relation='child_term_parent_term_rel',
        column1='parent_term_id', column2='child_term_id',
        string='Children Terms', copy=False)

    @api.one
    def set_relation_terms(self, parent_term_ids):
        vals = {
            'parent_m2m_ids': [[6, False, parent_term_ids]],
        }
        self.write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        Create a new term and notify it to the thesaurus to send a message to
        the followers.
        :param: vals
        :type: dictionary that contains at least 'name'
        :rparam: id of the new term
        :rtype: integer
        """
        if not vals.get('search_name'):
            vals['search_name'] = vals.get('name')
        new_id = super(ThesaurusTerm, self).create(vals)
        if not self.env.context.get('load_mode'):
            # Reset notification term on the thesaurus
            new_id.thesaurus_id.update_notification_term()
            # Set notification term on the thesaurus
            new_id.thesaurus_id.update_notification_term(newid=new_id.id)
        return new_id

    @api.multi
    def get_children_term(self):
        self.ensure_one()
        children_terms = []
        for t in self.children_m2m_ids:
            children_terms += t.get_children_term()
        children_terms.append(self.id)
        return list(set(children_terms))

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = list(args or [])
        if len(name) and name[-1:] == '!':
            name = name.replace('!', '', 1)
            args = [
                '|',
                ('name', '=', name),
                ('select_name', '=', name),
            ]
        else:
            ids = super(ThesaurusTerm, self).search([
                    '|',
                    ('select_name', operator, name),
                    ('search_name', operator, name),
                ] + args, limit=80)
            if ids:
                return ids.name_get()
        return super(ThesaurusTerm, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = default or {}
        default.update({
            'name': _('%s (copy)') % self.name,
        })
        return super(ThesaurusTerm, self).copy(default=default)

# view methods: onchange, button

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
        return self.write(vals)

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
    def button_reset(self, cr, uid, ids, context=None):
        """
        Cancel the term
        :rparam: True
        :rtype: boolean
        """
        self.ensure_one()
        return super(ThesaurusTerm, self).action_revalidate(
            vals={'state': TERM_AVAILABLE_STATES[0][0]})
