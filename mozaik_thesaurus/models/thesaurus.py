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
        ctx = self.env.context.copy()
        if not newid:
            # context: notrack when resetting the new term id to False to avoid
            # a notification
            ctx['mail_notrack'] = True
        vals = {'new_thesaurus_term_id': newid}
        return self.with_context(ctx).write(vals)


class ThesaurusTerm(models.Model):

    _name = 'thesaurus.term'
    _inherit = ['mozaik.abstract.model']
    _description = 'Thesaurus Term'
    _order = 'name'
    _unicity_keys = 'technical_name'

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

    @api.one
    @api.depends('name', 'state', 'expire_date')
    def _compute_technical_name(self):
        elts = [
            '%s' % self.thesaurus_id.id,
            self.state,
            self.state == 'draft' and self.name or
            self.state == 'confirm' and
            self.ext_identifier or self.expire_date
        ]
        self.technical_name = '#'.join([el for el in elts if el])

    name = fields.Char(
        string='Term', required=True, index=True, track_visibility='onchange')
    thesaurus_id = fields.Many2one(
        comodel_name='thesaurus', string='Thesaurus', readonly=True,
        required=True, default=_get_default_thesaurus_id)
    ext_identifier = fields.Char(
        string='External Identifier', required=False, index=True,
        track_visibility='onchange', states={'confirm': [('required', True)]})
    state = fields.Selection(
        selection=TERM_AVAILABLE_STATES, string='Status', readonly=True,
        required=True, track_visibility='onchange',
        default=TERM_AVAILABLE_STATES[0][0])
    technical_name = fields.Char(
        compute='_compute_technical_name', index=True, store=True)

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
        new_id = super(ThesaurusTerm, self).create(vals)
        if not self.env.context.get('load_mode'):
            # Reset notification term on the thesaurus
            self.thesaurus_id.update_notification_term()
            # Set notification term on the thesaurus
            self.thesaurus_id.update_notification_term(newid=new_id)
        return new_id

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = default or {}
        default.update({
            'ext_identifier': False,
            'state': TERM_AVAILABLE_STATES[0][0],
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
