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
        selection=CATEGORY_TYPE, index=True, string='Type',
        track_visibility='onchange')
    allow_multi = fields.Boolean(
        string='Allow Multiple Involvements',
        default=False, track_visibility='onchange')

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

    involvement_ids = fields.One2many(
        comodel_name='partner.involvement',
        inverse_name='involvement_category_id', string='Involvements')

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
    def write(self, vals):
        """
        Force an effective time on an allow_multi category
        """
        self.ensure_one()
        if vals.get('allow_multi'):
            invs = self.mapped('involvement_ids').filtered(
                lambda s: not s.effective_time)
            invs.write({'effective_time': fields.Datetime.now()})
        res = super(PartnerInvolvementCategory, self).write(vals)
        return res

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
        store=True, readonly=True, index=True)
    allow_multi = fields.Boolean(
        related='involvement_category_id.allow_multi',
        string='Allow Multiple Involvements',
        store=True, readonly=True)
    effective_time = fields.Datetime(
        string='Involvement Date', copy=False, track_visibility='onchange')
    creation_time = fields.Datetime(
        string='Involvement Date',
        compute='_compute_creation_time', store=True)

    _rec_name = 'involvement_category_id'

    _sql_constraints = [
        (
            'multi_or_not',
            'CHECK (allow_multi IS TRUE AND effective_time IS NOT NULL '
            'OR allow_multi IS FALSE)',
            'Effective time is mandatory '
            'for this kind of involvement category !',
        ),
    ]

    @api.multi
    @api.depends("effective_time")
    def _compute_creation_time(self):
        for involvement in self:
            if involvement.effective_time:
                involvement.creation_time = involvement.effective_time
            else:
                involvement.creation_time = involvement.create_date

    def init(self, cr):
        def create_index(i, index_def):
            createit = True
            query = \
                "SELECT indexdef " \
                "FROM pg_indexes " \
                "WHERE tablename = '%s' AND indexname = '%s_unique_%s_idx'"
            cr.execute(query % (self._table, self._table, i))
            sql_res = cr.dictfetchone()
            if sql_res:
                if sql_res['indexdef'] != index_def:
                    cr.execute(
                        "DROP INDEX %s_unique_%s_idx" % (self._table, i))
                else:
                    createit = False
            if createit:
                cr.execute(index_def)

        index1 = "CREATE UNIQUE INDEX %s_unique_1_idx " \
            "ON %s USING btree " \
            "(partner_id, involvement_category_id) " \
            "WHERE active IS TRUE AND allow_multi IS FALSE" \
            % (self._table, self._table)
        create_index(1, index1)

        index2 = "CREATE UNIQUE INDEX %s_unique_2_idx " \
            "ON %s USING btree " \
            "(partner_id, involvement_category_id, effective_time) " \
            "WHERE active IS TRUE AND allow_multi IS TRUE" \
            % (self._table, self._table)
        create_index(2, index2)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        '''
        Add interests to partner when creating an involvement
        Set effective date if any
        '''
        if not vals.get('effective_time'):
            ic = self.env['partner.involvement.category'].browse(
                vals['involvement_category_id'])
            if ic.allow_multi:
                vals['effective_time'] = fields.Datetime.now()
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
        if self.active and not self.allow_multi:
            raise ValidationError(
                _('An active involvement cannot be duplicated.'))
        res = super(PartnerInvolvement, self).copy(default=default)
        return res

    @api.onchange('allow_multi')
    def _onchange_allow_multi(self):
        if self.allow_multi and not not self.effective_time:
            self.effective_time = fields.Datetime.now()
