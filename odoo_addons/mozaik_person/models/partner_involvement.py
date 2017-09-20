# -*- coding: utf-8 -*-
# Copyright 2017 Acsone Sa/Nv
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

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
    res_users_ids = fields.Many2many(
        'res.users', relation='involvement_category_res_users_rel',
        column1='category_id', column2='user_id',
        string='Owners', required=True, copy=False,
        default=lambda s: s._default_res_users_ids())

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
    partner_involvement_category_id = fields.Many2one(
        'partner.involvement.category', string='Involvement Category',
        required=True, index=True, track_visibility='onchange')
    note = fields.Text(string='Notes', track_visibility='onchange')
    code = fields.Char(related='partner_involvement_category_id.code')

    _rec_name = 'partner_involvement_category_id'
    _unicity_keys = 'partner_id, partner_involvement_category_id'

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if self.active:
            raise ValidationError(
                _('An active involvement cannot be duplicated.'))
        res = super(PartnerInvolvement, self).copy(default=default)
        return res
