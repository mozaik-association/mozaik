# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

CATEGORY_TYPE = [
    ('petition', 'Petition'),
    ('donation', 'Donations Campaign'),
    ('voluntary', 'Voluntary Work'),
]


class PartnerInvolvementCategory(models.Model):

    _name = 'partner.involvement.category'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partner Involvement Category'
    _unicity_keys = 'name'

    @api.model
    def _default_res_users_ids(self):
        return self.env.user

    name = fields.Char(
        'Involvement Category',
        required=True,
        track_visibility='onchange',
    )
    code = fields.Char(
        copy=False,
        track_visibility='onchange',
    )
    note = fields.Text(
        'Notes',
        track_visibility='onchange',
    )
    involvement_type = fields.Selection(
        selection=CATEGORY_TYPE,
        string='Type',
        index=True,
        track_visibility='onchange',
    )
    allow_multi = fields.Boolean(
        'Allow Multiple Involvements',
        default=False,
        track_visibility='onchange',
    )

    res_users_ids = fields.Many2many(
        'res.users',
        relation='involvement_category_res_users_rel',
        column1='category_id',
        column2='user_id',
        string='Owners',
        required=True,
        copy=False,
        default=lambda s: s._default_res_users_ids(),
    )
    # interest_ids = fields.Many2many(
    #     'thesaurus.term',
    #     relation='involvement_category_term_interests_rel',
    #     column1='category_id',
    #     column2='term_id',
    #     string='Interests',
    # )
    involvement_ids = fields.One2many(
        'partner.involvement',
        'involvement_category_id',
        string='Involvements',
    )

    def init(self):
        """
        Create unit index based on code for active records.
        :return:
        """
        result = super().init()

        cr = self.env.cr
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

        return result

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
        res = super().write(vals)
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
        res = super().copy(default=default)
        return res

    @api.onchange('involvement_type')
    def _onchange_involvement_type(self):
        self.allow_multi = (self.involvement_type == 'donation')
