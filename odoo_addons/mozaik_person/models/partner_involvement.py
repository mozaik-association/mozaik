# -*- coding: utf-8 -*-
# Copyright 2017 Acsone Sa/Nv
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

CATEGORY_TYPE = [
    ('petition', 'Petition'),
    ('donation', 'Donations Campaign'),
    ('voluntary', 'Voluntary Work'),
]

_logger = logging.getLogger(__name__)


class PartnerInvolvementCategory(models.Model):

    _name = 'partner.involvement.category'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partner Involvement Category'

    @api.model
    def _default_res_users_ids(self):
        return self.env.user

    name = fields.Char(string='Involvement Category',
                       required=True,
                       track_visibility='onchange')
    code = fields.Char(copy=False,
                       track_visibility='onchange')
    note = fields.Text(string='Notes', track_visibility='onchange')
    involvement_type = fields.Selection(
        selection=CATEGORY_TYPE, index=True, string='Type')

    res_users_ids = fields.Many2many(
        comodel_name='res.users',
        relation='involvement_category_res_users_rel',
        column1='category_id', column2='user_id',
        string='Owners', required=True, copy=False,
        default=lambda s: s._default_res_users_ids())
    interests_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        relation='involvement_category_term_interests_rel',
        column1='category_id', column2='term_id',
        string='Interests',
    )

    _unicity_keys = 'name'

    def init(self, cr):
        createit = True
        index_def = "CREATE UNIQUE INDEX %s_unique_code_idx ON %s " \
                    "USING btree (code) WHERE (active IS TRUE)" % \
                    (self._table, self._table)
        cr.execute("""
            SELECT indexdef
            FROM pg_indexes
            WHERE tablename = '%s' and indexname = '%s_unique_code_idx'""" % (
            self._table, self._table))
        sql_res = cr.dictfetchone()
        if sql_res:
            if sql_res['indexdef'] != index_def:
                cr.execute("DROP INDEX %s_unique_code_idx" % (self._table,))
            else:
                createit = False

        if createit:
            cr.execute(index_def)

    @api.multi
    def copy(self, default=None):
        """
        Mark the name as (copy)
        Retrieve owner list if possible
        """
        default = default or {}
        default['name'] = _('%s (copy)') % self.name
        if self.env.user in self.res_users_ids:
            default['res_users_ids'] = [(6, 0, self.res_users_ids.ids)]
        res = super(PartnerInvolvementCategory, self).copy(default=default)
        return res


class PartnerInvolvement(models.Model):

    _name = 'partner.involvement'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partner Involvement'

    partner_id = fields.Many2one(
        'res.partner', string='Partner',
        required=True, index=True, track_visibility='onchange')
    involvement_category_id = fields.Many2one(
        'partner.involvement.category', string='Involvement Category',
        oldname='partner_involvement_category_id',
        required=True, index=True, track_visibility='onchange')
    note = fields.Text(string='Notes', track_visibility='onchange')
    involvement_type = fields.Selection(
        related='involvement_category_id.involvement_type',
        store=True, index=True)

    _rec_name = 'involvement_category_id'
    _unicity_keys = 'partner_id, involvement_category_id'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        '''
        Add interests to partner when creating an involvement
        '''
        res = super(PartnerInvolvement, self).create(vals)
        terms = res.involvement_category_id.interests_m2m_ids
        if terms:
            interests = [
                (4, term.id) for term in terms
            ]
            res.partner_id.suspend_security().write(
                {'interests_m2m_ids': interests})
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if self.active:
            raise ValidationError(
                _('An active involvement cannot be duplicated.'))
        res = super(PartnerInvolvement, self).copy(default=default)
        return res
